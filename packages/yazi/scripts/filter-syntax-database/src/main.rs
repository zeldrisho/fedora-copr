use serde::{Deserialize, Serialize, Serializer};
use std::{
    collections::{BTreeMap, HashMap},
    env, fs,
};
use syntect::{dumps, parsing::{Scope, ParseState, syntax_definition::{Context, ContextId, ContextReference, MatchOperation, Pattern}}};

type Result<T> = std::result::Result<T, Box<dyn std::error::Error>>;

// Mirror only the opaque ContextId layout from pinned Syntect 5.3.0.
#[derive(Deserialize, Serialize)]
struct Id {
    syntax_index: usize,
    context_index: usize,
}

#[derive(Deserialize, Serialize)]
struct LazyContexts {
    #[serde(serialize_with = "ordered_map")]
    context_ids: HashMap<String, ContextId>,
    contexts: Vec<Context>,
}

struct Mapping {
    indices: Vec<Option<usize>>,
    plain: Id,
    fallbacks: usize,
    context_counts: Vec<usize>,
}

/// Remap a context ID to retained syntax indices, using Plain Text for excluded syntaxes.
fn remap_id(id: &mut ContextId, mapping: &mut Mapping) -> Result<()> {
    let mut raw: Id = bincode::deserialize(&bincode::serialize(id)?)?;
    match mapping.indices.get(raw.syntax_index) {
        Some(Some(index)) => raw.syntax_index = *index,
        Some(None) => {
            // Excluded languages embedded in a retained grammar get no
            // highlighting; never retain their compiled contexts or patterns.
            raw.syntax_index = mapping.plain.syntax_index;
            raw.context_index = mapping.plain.context_index;
            mapping.fallbacks += 1;
        }
        None => return Err(format!("invalid syntax index {}", raw.syntax_index).into()),
    }
    if raw.context_index >= mapping.context_counts[raw.syntax_index] {
        return Err(format!("invalid context {} in syntax {}", raw.context_index, raw.syntax_index).into());
    }
    *id = bincode::deserialize(&bincode::serialize(&raw)?)?;
    Ok(())
}

// Syntect's non-exhaustive tuple variants cannot be matched externally.
#[derive(Deserialize, Serialize)]
enum Reference {
    Named(String),
    ByScope { scope: Scope, sub_context: Option<String>, with_escape: bool },
    File { name: String, sub_context: Option<String>, with_escape: bool },
    Inline(String),
    Direct(ContextId),
}

/// Remap direct context references while preserving unresolved reference variants.
fn remap_ref(reference: &mut ContextReference, mapping: &mut Mapping) -> Result<()> {
    let mut raw: Reference = bincode::deserialize(&bincode::serialize(reference)?)?;
    if let Reference::Direct(id) = &mut raw {
        remap_id(id, mapping)?;
    }
    *reference = bincode::deserialize(&bincode::serialize(&raw)?)?;
    Ok(())
}

/// Remap context IDs in lookups, prototypes, includes, and match operations.
fn remap_contexts(lazy: &mut LazyContexts, mapping: &mut Mapping) -> Result<()> {
    for id in lazy.context_ids.values_mut() {
        remap_id(id, mapping)?;
    }
    for context in &mut lazy.contexts {
        if let Some(id) = &mut context.prototype {
            remap_id(id, mapping)?;
        }
        for pattern in &mut context.patterns {
            match pattern {
                Pattern::Include(reference) => remap_ref(reference, mapping)?,
                Pattern::Match(pattern) => {
                    if let MatchOperation::Push(refs) | MatchOperation::Set(refs) = &mut pattern.operation {
                        for reference in refs { remap_ref(reference, mapping)?; }
                    }
                    if let Some(reference) = &mut pattern.with_prototype {
                        remap_ref(reference, mapping)?;
                    }
                }
            }
        }
    }
    Ok(())
}

#[derive(Deserialize, Serialize)]
struct SyntaxSet {
    syntaxes: Vec<SyntaxReference>,
    path_syntaxes: Vec<(String, usize)>,
}

#[derive(Deserialize, Serialize)]
struct SyntaxReference {
    name: String,
    file_extensions: Vec<String>,
    scope: Scope,
    first_line_match: Option<String>,
    hidden: bool,
    #[serde(serialize_with = "ordered_map")]
    variables: HashMap<String, String>,
    serialized_lazy_contexts: Vec<u8>,
}

/// Serialize map entries in key order for reproducible syntax dumps.
fn ordered_map<S, V>(map: &HashMap<String, V>, serializer: S) -> std::result::Result<S::Ok, S::Error>
where
    S: Serializer,
    V: Serialize,
{
    let ordered: BTreeMap<_, _> = map.iter().collect();
    ordered.serialize(serializer)
}

/// Check syntax and context indices, then parse runtime fixtures with every syntax.
fn validate(data: &[u8]) -> Result<()> {
    let set: SyntaxSet = dumps::from_uncompressed_data(data)?;
    let mut contexts: Vec<LazyContexts> = set.syntaxes.iter()
        .map(|syntax| dumps::from_reader(&syntax.serialized_lazy_contexts[..]))
        .collect::<std::result::Result<_, _>>()?;
    let mut identity = Mapping {
        indices: (0..contexts.len()).map(Some).collect(),
        plain: Id { syntax_index: 0, context_index: 0 },
        fallbacks: 0,
        context_counts: contexts.iter().map(|lazy| lazy.contexts.len()).collect(),
    };
    for (_, index) in &set.path_syntaxes {
        if *index >= contexts.len() { return Err("invalid path syntax index".into()); }
    }
    for (syntax, lazy) in set.syntaxes.iter().zip(&mut contexts) {
        remap_contexts(lazy, &mut identity).map_err(|error| format!("{}: {error}", syntax.name))?;
    }
    let loaded: syntect::parsing::SyntaxSet = dumps::from_uncompressed_data(data)?;
    for syntax in loaded.syntaxes() {
        for fixture in [
            include_str!("../fixtures/preview.toml"),
            "version = 4\n\n[[package]]\nname = \"example\"\nversion = \"1.0.0\"\n",
            "[section]\nkey=value\n; comment\n",
            "Hello, plain text!\n",
            "<html><style>body { color: red; }</style><script>const x = 1;</script></html>\n",
        ] {
            let mut state = ParseState::new(syntax);
            for line in fixture.split_inclusive('\n') {
                state.parse_line(line, &loaded).map_err(|error| format!("{}: {error}", syntax.name))?;
            }
        }
    }
    Ok(())
}

/// Filter excluded grammars or validate an existing database from command-line paths.
fn main() -> Result<()> {
    let mut args = env::args().skip(1);
    let input = args.next().ok_or("usage: yazi-syntax-filter INPUT OUTPUT")?;
    let output = args.next().ok_or("usage: yazi-syntax-filter INPUT OUTPUT")?;
    if args.next().is_some() {
        return Err("usage: yazi-syntax-filter INPUT OUTPUT".into());
    }

    if input == "--validate" {
        validate(&fs::read(output)?)?;
        eprintln!("All context references and runtime fixtures validated");
        return Ok(());
    }
    let data = fs::read(input)?;
    let mut set: SyntaxSet = dumps::from_uncompressed_data(&data)?;
    // This helper requires the original upstream database, never an already
    // filtered one with potentially stale indices.
    validate(&data)?;
    let excluded = [
        "hosts", "less", "livescript", "nginx", "verilog", "F#", "INI",
        "HTML (Jinja2)", "Jinja2", "Racket", "Todo.txt",
        "Fortran (Fixed Form)", "Fortran (Modern)", "Fortran Namelist",
        "GFortran Build Results", "OpenMP (Fortran)",
    ];
    let mut old_to_new = vec![None; set.syntaxes.len()];
    let matched: Vec<_> = excluded.iter().filter(|name| {
        set.syntaxes.iter().any(|syntax| syntax.name.eq_ignore_ascii_case(name))
    }).collect();
    let mut retained = Vec::with_capacity(set.syntaxes.len());
    for (old_index, syntax) in set.syntaxes.into_iter().enumerate() {
        if excluded.iter().any(|name| syntax.name.eq_ignore_ascii_case(name)) {
            continue;
        }
        old_to_new[old_index] = Some(retained.len());
        retained.push(syntax);
    }
    if old_to_new.iter().filter(|index| index.is_none()).count() != excluded.len() {
        let missing: Vec<_> = excluded.iter().filter(|name| !matched.contains(name)).collect();
        return Err(format!("input must contain every excluded grammar; missing {missing:?}; use the original upstream database").into());
    }
    set.syntaxes = retained;
    let plain_index = set.syntaxes.iter().position(|syntax| syntax.name == "Plain Text")
        .ok_or("database lacks Plain Text fallback")?;
    let plain: LazyContexts = dumps::from_reader(&set.syntaxes[plain_index].serialized_lazy_contexts[..])?;
    let plain_id = plain.context_ids.get("main").ok_or("Plain Text lacks main context")?;
    let mut mapping = Mapping {
        indices: old_to_new.clone(),
        plain: bincode::deserialize(&bincode::serialize(plain_id)?)?,
        fallbacks: 0,
        context_counts: set.syntaxes.iter().map(|syntax| {
            let lazy: LazyContexts = dumps::from_reader(&syntax.serialized_lazy_contexts[..])?;
            Ok(lazy.contexts.len())
        }).collect::<Result<_>>()?,
    };
    mapping.plain.syntax_index = plain_index;
    // Compiled lazy contexts contain IDs in prototypes, includes, Push/Set
    // operations, with_prototype, and their own named-context lookup tables.
    for syntax in &mut set.syntaxes {
        let mut lazy: LazyContexts = dumps::from_reader(&syntax.serialized_lazy_contexts[..])?;
        remap_contexts(&mut lazy, &mut mapping)
            .map_err(|error| format!("{}: {error}", syntax.name))?;
        syntax.serialized_lazy_contexts = dumps::dump_binary(&lazy);
    }
    set.path_syntaxes.retain_mut(|(_, index)| {
        if let Some(Some(new_index)) = old_to_new.get(*index) {
            *index = *new_index;
            true
        } else {
            false
        }
    });

    let retained_count = set.syntaxes.len();
    dumps::dump_to_uncompressed_file(&set, &output)?;
    let result = fs::read(&output)?;
    let loaded: syntect::parsing::SyntaxSet = dumps::from_uncompressed_data(&result)?;
    if loaded.syntaxes().len() != retained_count
        || loaded.syntaxes().iter().any(|syntax| {
            excluded
                .iter()
                .any(|name| syntax.name.eq_ignore_ascii_case(name))
        })
    {
        return Err("filtered syntax database failed runtime-format validation".into());
    }
    validate(&result)?;
    eprintln!("Retained and runtime-validated {} syntax definitions; {} excluded-language references use Plain Text", retained_count, mapping.fallbacks);
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    /// Construct a context ID using the pinned Syntect serialization layout.
    fn id(syntax_index: usize, context_index: usize) -> ContextId {
        bincode::deserialize(&bincode::serialize(&Id { syntax_index, context_index }).unwrap()).unwrap()
    }

    /// Create a mapping that removes one syntax and retains two with known context counts.
    fn mapping() -> Mapping {
        Mapping {
            indices: vec![Some(0), None, Some(1)],
            plain: Id { syntax_index: 0, context_index: 0 },
            fallbacks: 0,
            context_counts: vec![1, 3],
        }
    }

    /// Verify retained syntax indices change while context indices stay intact.
    #[test]
    fn remaps_retained_indices_and_preserves_context() {
        let mut value = id(2, 2);
        remap_id(&mut value, &mut mapping()).unwrap();
        let raw: Id = bincode::deserialize(&bincode::serialize(&value).unwrap()).unwrap();
        assert_eq!((raw.syntax_index, raw.context_index), (1, 2));
    }

    /// Verify excluded syntax references use Plain Text and increment the fallback count.
    #[test]
    fn excluded_context_falls_back_to_plain_main() {
        let mut value = id(1, 177);
        let mut mapping = mapping();
        remap_id(&mut value, &mut mapping).unwrap();
        let raw: Id = bincode::deserialize(&bincode::serialize(&value).unwrap()).unwrap();
        assert_eq!((raw.syntax_index, raw.context_index), (0, 0));
        assert_eq!(mapping.fallbacks, 1);
    }

    /// Verify out-of-range syntax and context indices are rejected.
    #[test]
    fn rejects_invalid_indices() {
        assert!(remap_id(&mut id(3, 0), &mut mapping()).is_err());
        assert!(remap_id(&mut id(2, 3), &mut mapping()).is_err());
    }
}
