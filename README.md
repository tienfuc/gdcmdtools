gdcmdtools
=========
Google drive command-line tools

Tools can be used to maintain files on Google Drive.


# Installation
 * Enable the following Google APIs in your Google APIs console(https://code.google.com/apis/console#:services)
   * Drive API
   * Fusion Tables API
 * Grant access to Google Drive
   1. Get the API client secrect file from your Google API console(https://code.google.com/apis/console#:access)
   1. Check the section "Client ID for installed applications", at the right side, click at the "Download JSON".
   1. Save the json file as .gdcmdtools.secrets in your home directory.
   1. Execute any tools from gdcmdtools tool set in a terminal, like: % ./gdput.py -t ft samples/sample.csv 
   1. You will see message like: INFO:gdcmdtools.base:Please visit the URL in your browser: https://accounts.google.com/o/oauth2/auth?scope=....
   1. Visit the URL with browser and allow the app accessing your Google Drive.
   1. Copy the code you see in your browser, then back to the terminal, paste the code and hit enter.
   1. Done, you won't be asked for the code again unless the credential expired.


## gdput
This tool can be used to upload files to Google drive as Spreadsheet,csv,fusion table,doc, etc.

### Usage
<pre>
usage: gdput.py [-h] [-s SOURCE_TYPE] [-l TARGET_TITLE]
                [-d TARGET_DESCRIPTION] [-f FOLDER_ID] [-p TYPE ROLE VALUE]
                [-t {ft,pt,ss,doc,raw,ocr,dr}]
                [--ft_latlng_column FT_LATLNG_COLUMN]
                [--ft_location_column FT_LOCATION_COLUMN]
                [--csv_column_define DEFINE1_DEFINE2_DEFINE3...]
                [-r {local,oob}]
                source_file

gdput v0.0.1 - gdcmdtools (Google Drive command line tools)

positional arguments:
  source_file           The file you're going to upload to Google Drive

optional arguments:
  -h, --help            show this help message and exit
  -s SOURCE_TYPE, --source_type SOURCE_TYPE
                        define the source file type by MIME type,
                        ex: "text/csv", or "auto" to determine the file type by file name
  -l TARGET_TITLE, --target_title TARGET_TITLE
                        specify the title of the target file
  -d TARGET_DESCRIPTION, --target_description TARGET_DESCRIPTION
                        specify the description of the target file
  -f FOLDER_ID, --folder_id FOLDER_ID
                        the target folder ID on the Google drive
  -p TYPE ROLE VALUE, --permission TYPE ROLE VALUE
                        set the permission of the uploaded file, could be:
                        type: user, group, domain, anyone
                        role: owner, reader, writer
                        value: user or group e-mail address,
                        or 'me' to refer to the current authorized user
                        ex: -p anyone reader me # set the uploaded file public-read
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

fusion table support (--target_type ft):
  --ft_latlng_column FT_LATLNG_COLUMN
                        specify the column header for latitude and longitude for the fusion table,
                        the column will be created automatically
  --ft_location_column FT_LOCATION_COLUMN
                        specify the location column header for the fusion table
  --csv_column_define DEFINE1_DEFINE2_DEFINE3...
                        define the columns type for each column of the csv file,
                        can be "string", "number", "datetime", or "location".
                        ex: has 4 columns in the csv file: "name", "age", "birthday", "address".
                        you can set --csv_column_define string_number_datetime_location
</pre>

### Example
    % python ./gdput.py photo.jpg                    # upload photo.jpg to gd without changing the format
    % python ./gdput.py -t ft samples/sample.csv     # upload a csv file to gd as fusion table
    % python ./gdput.py -t ss samples/sample.csv     # upload a csv file to gd as spreadsheet
    % python ./gdput.py -t ft --ft_location_column address  --ft_latlng_column latlng  samples/sample.csv 
                                              # upload a csv to gd as fusion table with geocoding the latitude longitude data according to the address rows
    % python ./gdput.py -p anyone reader me samples/sample.csv     
                                              # upload a csv file as Spreadsheet and set the file public-read



## gdget

get files from google drive


## Packages
  * ubuntu PPA: https://launchpad.net/~ctf/+archive/gdcmdtools



## License
BSD License.
