SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
python3 "$SCRIPT_DIR/../accuracy_test.py" \
    --horizon "10m" \
    --freq "30s" \
    --lookback "120m" \
    --method fourier \
    --method linear \
    --step 100 \
    --no_seasonality_metrics \
    --hourly_metrics 
