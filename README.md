# Cerfa filler django app

Originally inspired by [Zero-Waste-Paris/fill-cerfa-11580](https://github.com/Zero-Waste-Paris/fill-cerfa-11580), but extensively reworked to make it a standalone web app.

## HowTo

...

## Tips

Don't forget to append style to SVG templates to avoid margin:

```html
<style>
@page {
        size: A4; /* Change from the default size of A4 */
        margin: 0mm; /* Set margin on each page */
      }

</style>
```
