#echo "usage: ./run_extract.sh 0 ps 4"

source ./init.sh

INDEX=$1
TEST_NUM=test$FRAME
TEST_FOLDER=$2
WINDOW_SIZE=$3

IMAGE_FOLDER=$BASE_FOLDER_NIX/images/

BIN=1
SLIDE=2
echo "using bin: $BIN and stride: $SLIDE"

SCRIPT_PATH="$PYTHONPATH/src/auto_feature_extraction.py"

#echo "$SCRIPT_PATH -x $ROOT_FOLDER_NIX -t $IMAGE_FOLDER -i $INDEX -f $TEST_FOLDER -w $WINDOW_SIZE -r $BIN -s $SLIDE ./config/auto_feature_extraction_config.ini"
python $SCRIPT_PATH -x $ROOT_FOLDER_NIX -t $IMAGE_FOLDER -i $INDEX -f $TEST_FOLDER -w $WINDOW_SIZE -r $BIN -s $SLIDE ./config/auto_feature_extraction_config.ini
