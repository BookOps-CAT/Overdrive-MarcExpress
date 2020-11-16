# Overdrive-MarcExpress
 Scripts supporting switch to MarcExpress workflow

 ## Procedure
1. Create backdated file in the Overdrive Marketplace of all MarcExpress records (ME)
    a) merge records by format
    b) validate and enforce UTF-8 character encoding
2. Create a MARC file of all Overdrive records in Sierra
    a) validate and enforce UTF-8 encoding
3. Add 037$a with Overdrive Reserve ID  if missing from 856 field if present there
    a) use `populate_bpl_037.py` or `populate_nyp_037.py` script
4. Extract Reserve IDs, etc. from Sierra bibs
    a) use `extract_nyp_overdrive_no.py` script
