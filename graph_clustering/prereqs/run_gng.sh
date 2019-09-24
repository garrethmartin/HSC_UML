#echo "run_gng.sh 12500 ps 25 0"

source ./init.sh

#echo $CODE_FOLDER
GNG_PATH=$CODE_FOLDER/dotnetcore/GNG/GNGConsoleApp/bin/Release/netcoreapp2.0/GNGConsoleApp.dll

#MAX_NODES=$1
TEST_NAME=$1
INPUT_FOLDER=$ROOT_FOLDER/
BATCH_SIZE=$2
NUM_ITERATIONS=500
NUM_THREADS=7
ONLINE=false
SKY_AREAS=$INPUT_FOLDER/model_folders.txt
GRAPH_INIT=$INPUT_FOLDER/out.txt

OUTPUT_FOLDER=$ROOT_FOLDER/model$3/

if [ ! -d "$OUTPUT_FOLDER" ]; then
    mkdir $OUTPUT_FOLDER
fi
#echo $DOTNETBIN "$GNG_PATH" "$ROOT_FOLDER/config/atlas_gng_config" "--sky_areas" "$SKY_AREAS" "--input_folder" "$INPUT_FOLDER" "--test_name" "$TEST_NAME" "--max_nodes" "$MAX_NODES" "--num_iterations" "$NUM_ITERATIONS" "--num_threads" "$NUM_THREADS" "--npy" "false" "--batch_size" "$BATCH_SIZE" "--outputfolder" "$OUTPUT_FOLDER" "--online" "$ONLINE" "--graph_init" "$GRAPH_INIT"  #> $OUTPUT_FOLDER/$4_gng_log.txt
#$DOTNETBIN "$GNG_PATH" "$ROOT_FOLDER/config/atlas_gng_config" "--sky_areas" "$SKY_AREAS" "--input_folder" "$INPUT_FOLDER" "--test_name" "$TEST_NAME" "--max_nodes" "$MAX_NODES" "--num_iterations" "$NUM_ITERATIONS" "--num_threads" "$NUM_THREADS" "--npy" "false" "--batch_size" "$BATCH_SIZE" "--outputfolder" "$OUTPUT_FOLDER" "--online" "$ONLINE" "--graph_init" "$GRAPH_INIT"  #> $OUTPUT_FOLDER/$4_gng_log.txt

#echo $DOTNETBIN "$GNG_PATH" "$ROOT_FOLDER/config/atlas_gng_config" "--sky_areas" "$SKY_AREAS" "--input_folder" "$INPUT_FOLDER" "--test_name" "$TEST_NAME" "--max_nodes" "$MAX_NODES" "--num_iterations" "$NUM_ITERATIONS" "--num_threads" "$NUM_THREADS" "--npy" "false" "--batch_size" "$BATCH_SIZE" "--outputfolder" "$OUTPUT_FOLDER" "--online" "$ONLINE" "--graph_init" "$GRAPH_INIT"  #> $OUTPUT_FOLDER/$4_gng_log.txt

$DOTNETBIN "$GNG_PATH" "$ROOT_FOLDER/config/atlas_gng_config" "--sky_areas" "$SKY_AREAS" "--input_folder" "$INPUT_FOLDER" "--test_name" "$TEST_NAME" "--npy" "false" "--batch_size" "$BATCH_SIZE" "--outputfolder" "$OUTPUT_FOLDER" "--online" "$ONLINE" "--graph_init" "$GRAPH_INIT"  #> $OUTPUT_FOLDER/$4_gng_log.txt


