#echo "run_conncomps.sh <testname> <index> <modelfoldername> <hac_count> <hac_threshold>"
#echo "run_conncomps.sh ps 0 model0"

source ./init.sh

#mnt/e/candels/code/core/ConnComponents/ConnectedComponents/bin/Release/netcoreapp2.0

CODE_PATH=$CODE_FOLDER/dotnetcore/ConnComponents/ConnectedComponents/bin/Release/netcoreapp2.0/ConnectedComponents.dll

TEST_NAME=$1
INDEX=$2
INPUT_FOLDER=$ROOT_FOLDER
SKY_AREAS=sky_areas_$INDEX.txt
MODEL_FOLDER_NAME=$3
OUTPUT_FOLDER=$ROOT_FOLDER/$MODEL_FOLDER_NAME
MODEL_FOLDER_PATH=$ROOT_FOLDER
SAMPLES_FILE_NAME=samples.csv
POSITIONS_FILE_NAME=positions.csv
HAC_INDEX=$4
HAC_THRESHOLD=$5
HAC_MAPPING_FILE_NAME=gng_hac_mapping_$HAC_THRESHOLD\_$HAC_INDEX.txt
HAC_CENTRES_FILE_NAME=hac_cluster_centres_$HAC_THRESHOLD\_$HAC_INDEX.txt

if [ ! -d "$OUTPUT_FOLDER" ]; then
    mkdir $OUTPUT_FOLDER
fi

#echo "$CODE_PATH" "$ROOT_FOLDER/config/auto_conncomps.txt" "--index" "$INDEX" "--root_folder" "$ROOT_FOLDER" "--sky_areas" "$SKY_AREAS" "--input_folder" "$INPUT_FOLDER" "--test_name" "$TEST_NAME" "--outputfolder" "$OUTPUT_FOLDER" "--model_folder_name" "$MODEL_FOLDER_NAME" "--hac_index" $HAC_INDEX "--hac_mapping_file_name" $HAC_MAPPING_FILE_NAME "--hac_centres_file_name" "$HAC_CENTRES_FILE_NAME" #> $OUTPUT_FOLDER/$4_gng_log.txt

$DOTNETBIN "$CODE_PATH" "$ROOT_FOLDER/config/auto_conncomps.txt" "--index" "$INDEX" "--root_folder" "$ROOT_FOLDER" "--sky_areas" "$SKY_AREAS" "--input_folder" "$INPUT_FOLDER" "--test_name" "$TEST_NAME" "--outputfolder" "$OUTPUT_FOLDER" "--model_folder_name" "$MODEL_FOLDER_NAME" "--hac_index" $HAC_INDEX "--hac_mapping_file_name" $HAC_MAPPING_FILE_NAME "--hac_centres_file_name" "$HAC_CENTRES_FILE_NAME" "--model_base_path" "$MODEL_FOLDER_PATH" #> $OUTPUT_FOLDER/$4_gng_log.txt


