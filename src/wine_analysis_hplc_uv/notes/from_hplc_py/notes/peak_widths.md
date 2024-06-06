# Peak Widths

1. Evaluation height is calculated as peak maxima - peak prominence * rel_height. The more prominent the peak, the lower down the eval height.
2. draw a line at the evaluation height in both directions until:
    - the line intersects a slope
    - signal border
    - crosses the vertical position of the base
3. width is calculated as the distance between the endpoints defined in (2.). By definition the maximum width is the horizontal distance between the bases.

Currently, the width and the