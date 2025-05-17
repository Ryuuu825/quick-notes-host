# quick-note-host
Build a navigation page with a list of links to other markdown files, allowing u to navigate between them through web links. Also display your markdown & latex math expression in html.

just see this example:
https://Ryuuu825.github.io/quick-notes-host

## Usage
download `init.py` and `setting.json` to get started
```bash
curl https://raw.githubusercontent.com/Ryuuu825/quick-notes-host/refs/heads/master/init.py -O
curl https://raw.githubusercontent.com/Ryuuu825/quick-notes-host/refs/heads/master/setting.json -O
```

run `python3 init.py` and then publish all the markdown files and generated `index.html`, `nav_page.md` to your hosting services.

## Setting
- `base_url`: the base url of thats points to the root folder of your markdown files.
- `ignore_dir_name`: u may set it true when u use sth like cloudflare r2 that does not support subdir.
- `section`: select your subdir to be shown in the navigation page. you can leave it empty array to show all the subdirs.
- `exclude_files`: exclude some markdown from the navigation page, use relative path.
- `alias`: change the name of the file/dir in the navigation page. 
