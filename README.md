# Google Docs CMS

This is an experiment to allow embedding cleaned HTML from Google Docs in template files.  It might be most useful as e.g., a Twig function, but right now it's a Python script for processing all .html files in a directory.

## Usage

Source files must contain one or more tags to reference a (publically accessible) Google Doc:

```
{{ gd:1lXknhHMaDcY3f1KivG31P-rN7IH7Q_HhuPFBtCkZrB0 }}
```

To process a set of files containing these tags, feed the parent directory to the script:

```bash
./gdcms.py -s sample/src -d sample/dist
```

That's it.  The script will collect tags, pull in and clean HTML from Docs, and create a new set of output files with the complete HTML.