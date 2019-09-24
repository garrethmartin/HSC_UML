using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Configuration;
using Ideafixxxer.CsvParser;
using SampleHandlerLib;
using System.IO;

namespace ConnectedComponents
{
    class InputOutput
    {
        Config config = null;

        public String RootFolderPath;
        public String OutputFolderPath;

        public String PositionsFileName;
        public String ModelFolderPath;
        public String SamplesFileName;
        public String NodePositionsFileName;
        public String NodeToHACMappingFileName;
        public String HACCentresFileName;
        public bool UseCentroids;

        public Dictionary<int, int> NodeToHACMapping;
        public int MaxClusterId;

        public bool LogAllSamples;

        public String Metric;
        public int NumImages;

        public int HACIndex;

        public String AgglomFolderName;

        public String TestName;
        public String TestBasePath;

        public String DataspaceName;

        public int NumThreads;

        public double[] Mu;
        public double[] Std;

        public String SkyAreasFileName;
        public int Index;


        public InputOutput(Config config)
        {
            this.config = config;

            RootFolderPath = config.Get("root_folder");
            String modelBasePath = config.Get("model_base_path");

            Index = config.Int("index");
            TestName = config["test_name"];
            TestBasePath = RootFolderPath + TestName + "/output_" + Index.ToString() + "/";

            if (config.ContainsKey("use_centroids") && config.Bool("use_centroids"))
                UseCentroids = true;
            else
                UseCentroids = false;


            SamplesFileName = config.Get("samples_file_name");
            NodePositionsFileName = config.Get("node_positions_file_name");
            
            HACCentresFileName = config.Get("hac_centres_file_name");

            HACIndex = config.Int("hac_index");

            PositionsFileName = config.Get("positions_file_name");

            String modelFolderName = config.Get("model_folder_name");
            ModelFolderPath = modelBasePath + "/" + modelFolderName + "/";
            LogAllSamples = config.Bool("log_all_samples");
            if (LogAllSamples)
            {
                String muPath = ModelFolderPath + "mean.csv";
                String stdPath = ModelFolderPath + "std.csv";
                Mu = CsvParserHelper.LoadDoubles(muPath)[0];
                Std = CsvParserHelper.LoadDoubles(stdPath)[0];
            }
            //String ska = config.Get("sky_areas");
            //SkyAreasFileName = "/" + config.Get("sky_areas");
            SkyAreasFileName = config.Get("sky_areas");

            NodeToHACMappingFileName = config.Get("hac_mapping_file_name");

            NumThreads = config.Int("num_threads");

            Metric = config.Get("metric").ToLower();
            NumImages = config.Int("num_images");

            DataspaceName = config.Get("dataspace_name");

            AgglomFolderName = config.Get("hac_folder") + "/";

            NodeToHACMapping = LoadNodeToHACMapping();

            Dictionary<int, int>.ValueCollection vals = NodeToHACMapping.Values;
            MaxClusterId = vals.Max() + 1;
        }

        public Dictionary<int, int> LoadNodeToHACMapping()
        {
            String nodeToHACMappingFilePath = ModelFolderPath + AgglomFolderName + NodeToHACMappingFileName;
            Dictionary<int, int> gngHacClusterMapping = CsvParserHelper.LoadIntsDict(nodeToHACMappingFilePath);
            return gngHacClusterMapping;
        }

        public override string ToString()
        {
            String s1 = String.Format(" Index: {0} TestName: {1} SkyAreasFileName: {2} ModelFolderPath: {3}", Index, TestName, SkyAreasFileName,
                ModelFolderPath);
            return s1;
        }

        public List<SkyArea> LoadSkyAreas(int index, String skyAreasFileName, bool hasHeader)
        {
            var skyAreas = new List<SkyArea>();

            if (!File.Exists(skyAreasFileName))
                Console.WriteLine("sky areas file does not exist or path is wrong: {0}", skyAreasFileName);

            using (StreamReader sr = new StreamReader(skyAreasFileName))
            {
                String line = null;
                bool firstLine = true;
                while ((line = sr.ReadLine()) != null)
                {
                    if (line.Trim().Length == 0)
                        continue;

                    if (hasHeader && firstLine)
                    {
                        firstLine = false;
                        continue;
                    }
                    String[] cols = line.Split(new char[] { ',' });

                    int skyAreaId = Int32.Parse(cols[0].Trim());
                    String field = cols[1].Trim();
                    var skyArea = new SkyArea(skyAreaId, index, field);

                    skyAreas.Add(skyArea);
                }
            }

            /*
            // get file sizes

            foreach (SkyArea skyArea in modelSkyAreas)
            {
                String tempSamplesFilePath = GetSamplesFilePath(skyArea);
                ulong[] fileSize = HDF5Wrapper.GetHDF5FileSize(tempSamplesFilePath, this.DataspaceName);
                skyArea.NumSampleRows = fileSize[0];
                skyArea.NumSampleCols = fileSize[1];
            }
            */
            return skyAreas;
        }

        public String GetSamplesFilePath(SkyArea skyArea)
        {
            return TestBasePath + "output_" + Index + "/" + skyArea.Id + "/" + SamplesFileName;
        }

        public List<float[]> LoadSamples(List<SkyArea> modelSkyAreas)
        {
            ulong chunkSize = 500000;
            List<float[]> finalSamples = new List<float[]>();

            ulong totalAreaRows = 0;
            foreach (SkyArea modelSkyArea in modelSkyAreas)
            {
                totalAreaRows += modelSkyArea.NumSampleRows;

                ulong numRows = modelSkyArea.NumSampleRows;
                ulong numDims = modelSkyArea.NumSampleCols;

                ulong i = 0;
                ulong count = chunkSize;
                while (i < numRows)
                {
                    if (i + chunkSize >= numRows)
                        count = numRows - i;

                    List<float[]> samples = GetSamplesChunk(modelSkyArea, i, count, numDims, modelSkyArea.NumMaxRows, modelSkyArea.NumMaxCols);
                    finalSamples.AddRange(samples);

                    i += chunkSize;
                }
            }

            float[] first = finalSamples[0];
            int middleC = (int)finalSamples.Count / 2;
            float[] middle = finalSamples[middleC];
            float[] last = finalSamples[finalSamples.Count - 1];

            if ((int)totalAreaRows != finalSamples.Count)
            {
                String err = String.Format("ERROR  ERROR Partial HDF5 read, read different number of records. {0} {1}", totalAreaRows, finalSamples.Count);
                Console.WriteLine(err);
                throw new Exception(err);

            }
            return finalSamples;
        }

        public List<float[]> NormSamplesChunk(List<float[]> samples, ZScore z)
        {
            for (int i = 0; i < samples.Count; i++)
            {
                for (int j = 0; j < samples[0].Length; j++)
                {
                    samples[i][j] -= z.Mu[j];
                    samples[i][j] /= z.Std[j];
                }
            }
            return samples;
        }

        public List<float[]> GetSamplesChunk(SkyArea skyArea, ulong offset, ulong chunkSize, ulong ndims, ulong maxrows, ulong maxcols)
        {
            String samplesFilePath = GetSamplesFilePath(skyArea);
            float[,] data = null; // HDF5Wrapper.LoadPartialHDF5(samplesFilePath, DataspaceName, offset, chunkSize, ndims, maxrows, maxcols);
            List<float[]> listData = ConvertToList(data, (int)ndims);
            return listData;
        }

        public static List<float[]> ConvertToList(float[,] data, int numDims)
        {
            var newList = new List<float[]>();

            int numRows = data.Length / (int)numDims;

            for (int i = 0; i < numRows; i++)
            {
                float[] f = new float[numDims];
                for (int j = 0; j < numDims; j++)
                    f[j] = data[i, j];
                newList.Add(f);
            }

            return newList;
        }

    }
}
