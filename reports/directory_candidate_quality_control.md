# Source directory quality-control exceptions

Seven entries (DIR-0452 through DIR-0458) are editorial/navigation links rather than ski-area facility names. They were accidentally classified as Miyazaki resorts because the HTML parser retained the last prefecture heading.

- Raw directory candidate records: 458 (preserved for reproducibility)
- Clearly nonfacility editorial/navigation links: 7
- Candidate facility records after flagging these links: 451 (still unverified; includes closed/paused resorts)
- Official operating-resort census: not established by this data

Do not delete source rows or treat 451 as an official facility count. Fix the source parser and regenerate derived datasets with explicit exclusion flags rather than silently changing the cohort.
