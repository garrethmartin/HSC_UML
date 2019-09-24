#echo "run_agg.sh <modelindex>"

source ./init.sh

CODE_PATH=$CODE_FOLDER/dotnetcore/AgglomerativeClustering/AgglomerativeClustering/bin/Release/netcoreapp2.0/AgglomerativeClustering.dll

TEST_FOLDER=model$1
TEST_FOLDER_PATH=$ROOT_FOLDER/
CONFIG_FOLDER=$ROOT_FOLDER/config/
MODEL_FOLDER=/model$1/

echo "Using model folder: $MODEL_FOLDER"


if [ ! -f $ROOT_FOLDER_NIX/$MODEL_FOLDER/mean.csv ]; then
   echo "File not found! $ROOT_FOLDER_NIX/$MODEL_FOLDER/mean.csv"
   exit 1
fi

NUM_PS_FEATURES=`head -1 $ROOT_FOLDER_NIX/$MODEL_FOLDER/mean.csv | sed 's/[^,]//g' | wc -c`

#echo "ROOT_FOLDER: $ROOT_FOLDER   TEST_FOLDER: $TEST_FOLDER_PATH   NUM PS FEATURES: $NUM_PS_FEATURES"

$DOTNETBIN "$CODE_PATH" "$CONFIG_FOLDER/auto_agglom_config" "--root_folder" "$TEST_FOLDER_PATH/" "--num_powerspectrum_features" "$NUM_PS_FEATURES" "--model_folder" "$MODEL_FOLDER" > $ROOT_FOLDER_NIX/$MODEL_FOLDER/agg_log.txt
