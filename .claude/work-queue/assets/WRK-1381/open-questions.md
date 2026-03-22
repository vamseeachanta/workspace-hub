# Open Questions: WRK-1381

1. What exact unit-normalization strategy should the canonical GZ fixture schema use?
2. Is the missing shared digitized-curve artifact expected to be created in `workspace-hub`,
   consumed from there by `digitalmodel`, or duplicated?
3. Where do the referenced source-side artifacts currently live, if they are not under the
   active workspace root?
4. Does the acceptance target count unique vessels/conditions only, or can same-vessel
   variants with different KG/displacement count toward the `>= 10` requirement?
