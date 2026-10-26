# Step 3 - Verify the rebuild
Tool: CadQuery + trimesh. Builds the Step 2 script, lists its faces, matches each dataset face by type/radius/centroid (-> side table), then checks face count, volume, bounding box and mean surface distance to the dataset mesh. Output: `output/verify_part_N.json`, `output/part_N_rebuilt_mesh.json` (per-triangle dataset face id).
