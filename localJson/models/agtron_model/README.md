# Agtron Color Prediction Demo

This package contains all the necessary files to run the Agtron color prediction demo, which demonstrates how to predict coffee bean color values from roast profiles.

## Contents

- `agtron_demo_standalone.py`: The main demo script that showcases the entire prediction process
- `sample/`: Directory containing sample roast files (.alog) to test with
- Model files:
  - `moe_model.pkl`: Combined Mixture of Experts model
  - `gmm.pkl`: Gaussian Mixture Model component
  - `scaler.pkl`: Feature scaler
  - `feature_cols.pkl`: Feature column names
  - `product_offsets.pkl`: Product-specific offset values
  - `expert_0.pkl` to `expert_4.pkl`: Individual expert models

## Requirements

- Python 3.7+
- Required packages:
  - numpy
  - pandas
  - matplotlib
  - scikit-learn (only if you decompress the combined model)

## How to Run

1. Make sure you have all the required Python packages installed
2. Run the demo with a sample roast file:

```bash
python agtron_demo_standalone.py sample/20241107_095209.alog
```

## Expected Output

- The demo will read the roast file and extract time and temperature data
- It will calculate roast features needed for prediction
- It will load the prediction model and predict the Agtron color value
- If the roast file contains a ground truth value, it will compare the prediction with the actual value
- A visualization of the roast profile will be saved as `roast_profile_demo.png`

## File Format

This demo works with Artisan Roaster Scope log files (.alog), which are Python dictionary-like structures containing:
- `timex`: List of time points in seconds
- `temp2`: List of bean temperature readings
- `title`: Product/bean name
- `roastvalue`: List containing Agtron color values

## Customization

You can use this demo with your own .alog files by providing the path to your file:

```bash
python agtron_demo_standalone.py path/to/your/roast/file.alog
```

## Notes

- If you don't have a Chinese font installed, the script will fall back to using English labels
- The prediction model was trained on data from a BuhlerRM60 roaster, so results may vary with other roaster types
- The visualization will automatically identify key points in the roast profile, such as turning point and first crack 