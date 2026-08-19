# Native format supersession notice

The wrapper-based ODG and PPTX assets distributed in the earlier v3.1 figure archive are superseded for editing purposes. They embedded each SVG as a single vector object and did not permit reliable object-level editing.

The v3.2 native files in this repository candidate decompose the figures into editable text boxes, geometric shapes, lines, curves and arrowheads. The canonical SVG sources themselves are unchanged.

Use only files containing `NATIVE_EDITABLE` when editing ODG or PPTX derivatives.
