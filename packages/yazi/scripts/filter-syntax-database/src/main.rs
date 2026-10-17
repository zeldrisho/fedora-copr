use serde::{Deserialize, Serialize, Serializer};
use std::{
    collections::{BTreeMap, HashMap},
    env, fs,
};
use syntect::{dumps, parsing::Scope};

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

fn ordered_map<S>(map: &HashMap<String, String>, serializer: S) -> Result<S::Ok, S::Error>
where
    S: Serializer,
{
    let ordered: BTreeMap<_, _> = map.iter().collect();
    ordered.serialize(serializer)
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut args = env::args().skip(1);
    let input = args.next().ok_or("usage: yazi-syntax-filter INPUT OUTPUT")?;
    let output = args.next().ok_or("usage: yazi-syntax-filter INPUT OUTPUT")?;
    if args.next().is_some() {
        return Err("usage: yazi-syntax-filter INPUT OUTPUT".into());
    }

    let data = fs::read(input)?;
    let mut set: SyntaxSet = dumps::from_uncompressed_data(&data)?;
    let excluded = ["hosts", "less", "livescript", "nginx", "verilog"];
    let mut old_to_new = vec![None; set.syntaxes.len()];
    let mut retained = Vec::with_capacity(set.syntaxes.len());
    for (old_index, syntax) in set.syntaxes.into_iter().enumerate() {
        if excluded.iter().any(|name| syntax.name.eq_ignore_ascii_case(name)) {
            continue;
        }
        old_to_new[old_index] = Some(retained.len());
        retained.push(syntax);
    }
    set.syntaxes = retained;
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
    eprintln!("Retained and validated {} syntax definitions", retained_count);
    Ok(())
}
