import pe
from pe.actions import Pack

# This grammar may be fragile against non PWN-3.0 versions of wordnet!
# _gloss_pe = pe.compile(
#     """
#     Start      <- ~Definition (DELIM Example)* EOS
#     Definition <- ( !DELIM (![(] . / Paren) )+
#     Paren      <- '(' (![)] .)* ')'    # assume parentheticals are closed
#     Example    <- ~(Quote (NonQuote Quote?)*) SPACE*
#     Quote      <- ["] InQuote* ["]     # regular string
#                 / ["] InQuote* EOS     # missing end-quote
#                 / !DELIM InQuote* ["]  # missing start-quote
#     InQuote    <- !["] .               # non-quote chars
#                 / ["] [A-Za-z]         # correcting for typos (e.g., 'I"m')
#     NonQuote   <- (!DELIM . (',' SPACE* &["])?)+
#     DELIM      <- [;:,] SPACE* &["]
#     SPACE      <- ' '
#     EOS        <- !.
#     """,
#     flags=(pe.MEMOIZE | pe.OPTIMIZE),
# )

gloss_parser = pe.compile(
    """
    Start       <- SPACE* Gloss EOS

    # Ideally definitions are delimited from examples with ;, but often
    # they are not, or the definition is missing.
    Gloss       <- Definition DELIM Examples
                 / Definition Examples
                 / ~"" Examples

    # Definitions are not always unquoted content. Sometimes they have
    # e.g. "examples" in the definition, parentheticals, and spurious
    # quotation marks.
    Definition  <- !["] ~( ( !DELIM DefContent )+ ["]? ) SPACE*
    DefContent  <- [Ee] '.'? [Gg] '.'? DELIM?  # e.g., eg: E.g.; etc.
                 / '(' (![)] .)* ')'    # assume parentheticals are closed
                 / &( ["] ( ALPHANUM / [`'] ) ) Quote
                 / ALPHANUM ["] &( ( SPACE+ / DELIM / EOS ) !["] )  # things like '13" cards'
                 / !["] .

    # Examples can be delimited with various punctuation or 'or'. Other
    # non-quoted content between quoted segments is often things like
    # "they said". Occasionally examples are missing the final quote.
    Examples    <- Example ( ( DELIM / SPACE* &["] ) Example )*
                 / ''
    Example     <- ~( Quote ( NonQuote Quote? )* ( ["] &( DELIM / SPACE* EOS) )? )
                 / ~( ["] .* )

    # Quoted segments sometimes have extra quotation marks
    Quote       <- ["] ["]? InQuote* ["] (["] !ALPHANUM)?
    InQuote     <- !["] .               # non-quote chars
                 / ["] ALPHANUM         # correcting for typos (e.g., 'I"m')
    NonQuote    <- SPACE* (!(DELIM / ["]) . )+ [,]? SPACE*

    DELIM       <- SPACE* [;:,] SPACE* &["]
    ALPHANUM    <- [0-9A-Za-z]
    SPACE       <- ' '
    EOS         <- !.
    """,
    actions={
        "Examples": Pack(list),
    },
    flags=(pe.MEMOIZE | pe.OPTIMIZE),
)
