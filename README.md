# Environmental-Modelling-Process

### Assignments

Because I had trouble finding the assignments in longer notebooks, I introduced a more visually pronounced style. To do so, the assignment must be written as HTML in the markdown cell. 

The HTML code:

```html
<div style="background:LightSkyBlue;border:1mm solid blue;padding:1%">
    <h4><span>&#129300 </span>Your Turn: Assignment Title</h4>
    <ol>
        <li>Assignment 1</li>
        <li>Assignment 2</li>
    </ol>
</div>
```
gives a cell that looks like this:

![](example.png)

### Zipping the Tutorial Files

Because manual zipping of all tutorial files is annoying, I added a short script that automates this job. - David

Using default options, the script zips each tutorial folder (matched using the pattern option) individually and places the resulting archives in the respective folders. Make sure, that the script is in the parent directory of the tutorial folders. Otherwise you can specifiy the path to the tutorial folder(s) as an argument.

```bash
python zipme.py [base_directory] --pattern=[GEE-SE03-Txx]
```

You can also specify an output folder:
```bash
python zipme.py --output=[output_directory]
```

To see what the script would do without performing the operations, add a `--test` flag.

### Protecting Cells in the Notebooks

Because I think that students should not alter markdown cells, and more importantly code cells that provide functionality using `ipywidgets`, I added a script to protect these cells in all tutorial notebooks. It disables the _editable_ attribute for all markdown and code cells that start with the string `# DO NOT ALTER`, which it also collapses. - David

I suggest that the script is run before the tutorial files are passed to the students. When no notebook path is given, it protects all notebooks in the base directory.

```bash
python protect.py [notebook_path]
```

When you want to edit the notebooks again, you can either disable the protection using _Jupyter Lab_ or by running the command:

```bash
python protect.py --unprotect
```

A `--test` flag is also available.