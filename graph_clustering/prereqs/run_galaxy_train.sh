#echo "run_galaxy_train.sh kmeans|agg model0 objectcounts.txt"

source ./init.sh

SCRIPT_PATH=$PYTHONPATH/src/galaxy_train_multi_param.py
ALGO=$1
MODEL_FOLDER=$2
INPUT_FOLDER=$ROOT_FOLDER_NIX/$MODEL_FOLDER/conncomps/
COUNTS_PATH=$INPUT_FOLDER/$3
OUTPUT_FOLDER=$INPUT_FOLDER
K_MIN=2
K_MAX=220
K_STEP=2
MIN_PIXELS=15
COL_OFFSET=1

python $SCRIPT_PATH -a $ALGO -c "$COUNTS_PATH" -m $MIN_PIXELS -k $K_MIN -e $K_MAX -s $K_STEP -o $COL_OFFSET -l gal_train.log -x "$OUTPUT_FOLDER"



