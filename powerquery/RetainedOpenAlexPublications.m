// Optional typed source view; canonical publication membership stays upstream.
// Deploy alongside fnProjectRetainedOpenAlex after native archive acceptance.
let
    // The native shared accessor currently allows only PubMed/DORA. Reuse its
    // underlying source-scoped reader without changing that shared whitelist.
    Observations=fnReadCommittedHistory(RetainedArchiveFiles,"OpenAlex")
in fnProjectRetainedOpenAlex(Observations)
