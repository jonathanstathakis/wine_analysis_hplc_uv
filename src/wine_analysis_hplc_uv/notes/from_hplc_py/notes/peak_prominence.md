# Peak Prominence

Peak prominence is defined as the difference of the peak maxima and its lowest contour line.
 
Peak prominence calculation method:
1. Define window interval
    - extend a a horizontal line left or right of the peak maxima.
    - the extension stops either at a window bound ('wlen') or when the line encounters the slope again.
2. Define signal left and right bases.
    - find signal minima for the left and right window bound.
3. Calculate prominence
    - the higher of the left or right base is defined as the lowest contour line of the peak.
    - prominence is calculated as the difference between the peak maxima and its lowest contour line.