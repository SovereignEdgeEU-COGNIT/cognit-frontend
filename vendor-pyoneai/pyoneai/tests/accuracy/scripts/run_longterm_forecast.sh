SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
python3 "$SCRIPT_DIR/../accuracy_test.py" \
    --horizon "48h" \
    --freq "1h" \
    --lookback "96h" \
    --method fourier \
    --method linear \
    --step 200 \
    --no_seasonality_metrics \
    --daily_metrics \
    --weekly_metrics \
    --plot_all
