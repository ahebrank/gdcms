# Google Docs CMS

This is an experiment to allow embedding content from Google Drive in templates.  Such content might be a chunk of HTML from a Google Doc or structured data from a Google Sheet.

This type of template tag might be most useful as e.g., a Twig function, but right now it's a Python script that batch processes all *.html templates within a parent directory.

## Template Tags

gdcms template tags indicate what kind of document to fetch (`gd` = Google Doc, `gs` = Google Sheet) and identify the document by the document ID, the long string of characters that appear in any shared Google Doc link. The Sheets tags also contain references to a specific content element and field.

gdcms doesn't current deal with authentication, so any Google Doc referenced must be publicly accessible.  The easiest way to ensure a doc is publicly available is to use the File -> Publish to Web menu link.

### Embedding HTML from a Google Doc

To insert a chunk of cleaned HTML from a Google Doc, a template tag similar to the following should appear in your markup:

```
{{ gd:1lXknhHMaDcY3f1KivG31P-rN7IH7Q_HhuPFBtCkZrB0 }}
```

### Embedding structured data from a Google Sheet

Set up one or more sheets in which the first row contains field IDs and the first column contains element IDs.

For instance,

| id      | heading           | subheading            |
| ------- | ----------------- | ----------------------|
| page-1  | Title for Page 1  | Subheading for page 1 |
| page-2  | Title for Page 2  | Subheading for page 2 |

Template tags then reference the Sheet, element ID, and field ID as a sort of pseudo-function.

For instance, the tag:

```
{{ gs:1czrB7gV7ySSEyj0keNA6yoXF6PC1HoRLHfdW2yZXoLc(page-1, heading) }}
```

would return 'Title for Page 1' (the `heading` field for the `page-1` row).

## Usage

To process a set of files containing these tags, feed the parent directory to the script:

```bash
./gdcms.py -s sample/src -d sample/dist
```

That's it.  The script will collect tags, pull in markup and structured data, and create a new set of output files with the complete HTML.

For more command line options,

```bash
./gdcms.py -h
```