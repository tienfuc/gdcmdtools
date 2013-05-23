gdcmdtools
=========
Google drive command-line tools


# Install

 * Get the API client secrect file from your Google API console.(https://code.google.com/apis/console#:access)
 * Check the section "Client ID for installed applications", at the right side, click at the "Download JSON".
 * Save the json file as .gdcmdtools.secrets in your home directory.
 * Execute any tools from gdcmdtools tool set in a console, like: % ./gdput.py -t ft samples/sample.csv 
 * You will see message like: INFO:gdcmdtools.base:Please visit the URL in your browser: https://accounts.google.com/o/oauth2/auth?scope=....
 * Visit the URL with browser and allow access from the app.
 * Copy the code you see in your browser, then back to the console, input the code and hit enter.
 * Done, you won't be asked for the code again unless the credential expired.


## gdput

### Usage
<pre>
usage: gdput.py [-h] [-s SOURCE_TYPE] [-l TARGET_TITLE]
                [-d TARGET_DESCRIPTION] [-f FOLDER_ID]
                [-t {ft,pt,ss,doc,raw,ocr,dr}]
                [--ft_latlng_column FT_LATLNG_COLUMN]
                [--ft_location_column FT_LOCATION_COLUMN] [-r {local,oob}]
                source_file

gdput v0.0.1 - gdcmdtools (Google Drive command line tools)

positional arguments:
  source_file           The file you're going to upload to Google Drive

optional arguments:
  -h, --help            show this help message and exit
  -s SOURCE_TYPE, --source_type SOURCE_TYPE
                        define the source file type by MIME type, ex: "text/csv", or "auto" to determine the file type by file name
  -l TARGET_TITLE, --target_title TARGET_TITLE
                        specify the title of the target file
  -d TARGET_DESCRIPTION, --target_description TARGET_DESCRIPTION
                        specify the description of the target file
  -f FOLDER_ID, --folder_id FOLDER_ID
                        the target folder ID on the Google drive
  -t {ft,pt,ss,doc,raw,ocr,dr}, --target_type {ft,pt,ss,doc,raw,ocr,dr}
                        define the target file type on Google Drive, could be:
                        raw: (default) the source file will uploaded without touching
                        ft: Fusion Table (for .csv)
                        pt: Presentation (for .ppt, .pps, .pptx)
                        ss: Spreadsheet (for .xls, .xlsx, .ods, .csv, .tsv, .tab)
                        doc: Document (for .doc, .docx, .html, .htm, .txt, .rtf)
                        ocr: OCR (for .jpg, .git, .png, .pdf)
                        dr: Drawing (for .wmf)
  -r {local,oob}, --redirect_uri {local,oob}
                        specify the redirect URI for the oauth2 flow, could be:
                        local: means "http://localhost"
                        oob: (default) means "urn:ietf:wg:oauth:2.0:oob"

fusion table geocoding:
  --ft_latlng_column FT_LATLNG_COLUMN
                        specify the column header for latitude and longitude for the fusion table(if target_type is ft and --ft_location_column is used), the column will be created if not present
  --ft_location_column FT_LOCATION_COLUMN
                        specify the location column header for the fusion table (if target_type is ft)

</pre>

### Example

    % ./gdput.py -t ft samples/sample.csv     # upload a csv file to gd as fusion table
    % ./gdput.py -t ss samples/sample.csv     # upload a csv file to gd as spreadsheet
    % ./gdput.py -t ft --ft_location_column address  --ft_latlng_column latlng  samples/sample.csv 
                                              # upload a csv to gd as fusion table with latitude longitude data(will be generated automatically)



## gdget

get files from google drive
