using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Configuration;
using System.IO;
using System.Runtime.InteropServices;
using System.Text.RegularExpressions;
using CsvParser;
using GNG;


namespace GNGConsoleApp
{
    public class InputOutputData
    {
        
        public String BasePath;
        public String SamplesFilePath;
        public String SamplesFolderPath;
        public String SamplesFileName;
        public String OutputPath;
        public String TestBasePath;
        public String DataspaceName;
        public int BatchSize;
        public String Classification;
        

        public float[] Mu;
        public float[] Std;

        public int NumDimensions;

        public int MaxNodes;
        public int NumEpochs;
        public int NumThreads;
        public int Metric;
        public bool MeanNormalize;
        public bool MeanAndUnitNormalize;
        public bool OutputToLog;
        public bool WriteIntermediateFiles;
        public bool CalculateQuantError;
        public bool LogAllSamples;
        //public bool HDF5;
        public bool NPY;
        public bool MultipleSkyAreas;

        public bool DeDupe;
        public int DeDupePrecision;

        public bool Online;
        public List<float[]> InitNodes;
        public List<double[]> InitNodeInfo;
        public List<int[]> InitEdges;
        public List<int[]> InitMetaInfo;

        public double[] PartialMean;
        public List<double[]> PartialStd;
        public int TotalSamples;

        public Dictionary<String, List<int>> OkIndicies;

        public List<SkyArea> SkyAreas;

        Config config = null;
        internal InputOutputData(Config config)
        {
            this.config = config;
        }

        public void Init()
        {
            BasePath = config.Get("input_folder"); 
            SamplesFolderPath = BasePath;
            SamplesFilePath = BasePath + config.Get("samples_file_name"); 
            SamplesFileName = config.Get("samples_file_name");
            MaxNodes = config.Int("max_nodes");
            NumEpochs = config.Int("num_iterations");
            NumThreads = config.Int("num_threads");
            Metric = config.Int("metric");
            
            DataspaceName = config["dataspaceName"];
            MeanNormalize = config.Bool("mean_normalize");
            MeanAndUnitNormalize = config.Bool("zscore_normalize");
            LogAllSamples = config.Bool("log_samples");
            if (MeanNormalize && MeanAndUnitNormalize)
                throw new Exception("Config Error: Only one of mean_normalize and zscore_normalize allowed");
            OutputToLog = config.Bool("output_log");
            WriteIntermediateFiles = config.Bool("write_intermediate");
            CalculateQuantError = config.Bool("quantisation_error");

            MultipleSkyAreas = config.Bool("multiple_sky_areas");

            TestBasePath = BasePath;

            String skyAreasFileName = config["sky_areas"];

            SkyAreas = LoadSkyAreas(skyAreasFileName);

            DeDupe = true;
            DeDupePrecision = 0;

            if (config.ContainsKey("batch_size"))
                BatchSize = config.Int("batch_size");
            else
                BatchSize = -1;

            if (config.ContainsKey("classification"))
                Classification = config["classification"];
            else
                Classification = "";

            if (config.ContainsKey("npy"))
                NPY = config.Bool("npy");
            else
                NPY = false;

            OutputPath = config.Get("outputfolder");
            if (Classification.Length > 0)
                OutputPath = OutputPath + Classification + "/";
            if (!File.Exists(OutputPath))
                Directory.CreateDirectory(OutputPath);

            Online = false;
            if (config.ContainsKey("online") &&
                config.ContainsKey("graph_init") &&                
                config.Bool("online") == true)
            {
                String initGraphFolder = config.Get("graph_init");
                if (Directory.Exists(initGraphFolder) && File.Exists(initGraphFolder + "/meta.txt"))
                {
                    Console.WriteLine("Loading init nodes, nodeinfo and edges: {0}", initGraphFolder);
                    InitEdges = CsvParserHelper.LoadInts(initGraphFolder + "/edge_index.txt");
                    InitNodes = CsvParserHelper.LoadFloats(initGraphFolder + "/node_position_list.txt");
                    InitNodeInfo = CsvParserHelper.LoadDoubles(initGraphFolder + "/node_info.txt");
                    InitMetaInfo = CsvParserHelper.LoadInts(initGraphFolder + "/meta.txt");

                    List<double[]> partialMean = CsvParserHelper.LoadDoubles(initGraphFolder + "/partial_mean.csv");
                    PartialMean = partialMean[0];
                    PartialStd = CsvParserHelper.LoadDoubles(initGraphFolder + "/partial_std.csv");
                    List<int[]> numSamples = CsvParserHelper.LoadInts(initGraphFolder + "/partial_mean_sample_count.csv");
                    TotalSamples = numSamples[0][0];


                    Online = true;
                }
                else
                {
                    Console.WriteLine("ERROR Online true, but files don't exist: {0}", initGraphFolder);

                }
            }

            Console.WriteLine(ToString());
        }

        public override string ToString()
        {
            String s1 = String.Format("maxNodes: {0} numepochs: {1} numThreads: {2} metric: {5} mean_normalize: {3} zscore_normalize: {4} NPY: {5} ",
                MaxNodes, NumEpochs, NumThreads, MeanNormalize, MeanAndUnitNormalize, Metric, NPY);
            String s2 = String.Format("BasePath: {0} TestBasePAth: {1} DataspaceName {2} ", 
                BasePath, TestBasePath, DataspaceName);
            String s3 = String.Format(" log samples: {0}", LogAllSamples);
            return s1 + s2 + s3;
        }

        public static List<float[]> LoadSamples(String filePath)
        {
            Console.WriteLine("Loading Samples...");

            List<float[]> data = new List<float[]>();
            string[][] s;
            using (TextReader tr = File.OpenText(filePath))
            {
                CsvParser.CsvParser parser = new CsvParser.CsvParser();
                s = parser.Parse(tr);
            }
            int ndim = s[0].Length;
            foreach (string[] ssample in s)
            {
                float[] sample = new float[ndim];
                for (int i = 0; i < ndim; i++)
                {
                    sample[i] = float.Parse(ssample[i]);
                }
                data.Add(sample);
            }

            Console.WriteLine("Loaded {0} Samples", data.Count);
            return data;
        }

        public static void OutputLog(List<int[]> info, List<double[]> quantisation_error)
        {
            Console.WriteLine("********* summary *******");
            foreach (int[] line in info)
            {
                Console.WriteLine("{0}\t{1}\t{2}\t{3}\t{4}", line[0], line[1], line[2], line[3], line[4]);
            }

            Console.WriteLine("********* quantisation error *****");
            foreach (double[] error in quantisation_error)
            {
                Console.WriteLine("{0},{1}", error[0], error[1]);
            }
        }

        public static void SaveDataIntermediate(String basePath, List<float[]> samples, Graph g, List<List<GraphNode>> connectedComps, int input_dim, int iter = 0)
        {
            basePath += "/backup";
            if (!Directory.Exists(basePath))
                Directory.CreateDirectory(basePath);
            var clusters = connectedComps;
            GraphHelper gh = new GraphHelper(g, input_dim);
            int[,] nodeClusterIndex = gh.GetNodeClusterIndex(clusters);
            List<float[]> clusterCentres = gh.GetClusterCenters(clusters, nodeClusterIndex);
            List<float[]> codeVectors = gh.GetNodePositions();
            List<float[]> edges = gh.GetEdges(codeVectors);
            int[,] edgeIndex = gh.GetEdgeIndex();

            SaveTxt(basePath + String.Format("/node_cluster_index_{0}.txt", iter), nodeClusterIndex, 2);
            SaveTxt(basePath + String.Format("/cluster_centeres_{0}.txt", iter), clusterCentres);
            SaveTxt(basePath + String.Format("/node_position_list_{0}.txt", iter), codeVectors, colDelimiter: ',');
            SaveTxt(basePath + String.Format("/edge_index_{0}.txt", iter), edgeIndex, 2);
            SaveTxt(basePath + String.Format("/edges_{0}.txt", iter), edges, colDelimiter: ',');
        }

        public static void SaveData(String basePath, List<float[]> samples, Graph g, List<List<GraphNode>> connectedComps, int input_dim)
        {
            Console.WriteLine("Saving data");

            var clusters = connectedComps;
            GraphHelper gh = new GraphHelper(g, input_dim);
            Console.WriteLine("Retrieving NCI");
            int[,] nodeClusterIndex = gh.GetNodeClusterIndex(clusters);
            Console.WriteLine("Retrieving cluster centres");
            List<float[]> clusterCentres = gh.GetClusterCenters(clusters, nodeClusterIndex);
            Console.WriteLine("Retrieving node positions");
            List<float[]> codeVectors = gh.GetNodePositions();

            String nodeClusterIndexPath = basePath + "/node_cluster_index_.txt";
            String datapointClusterIndexPath = basePath + "/datapoint_cluster_index.txt";
            String datapointNodeIndexPath = basePath + "/datapoint_node_index.txt";
            String clusterCentresPath = basePath + "/cluster_centeres.txt";
            String codeVectorsPath = basePath + "/node_position_list.txt";
            String edgeIndexPath = basePath + "/edge_index.txt";
            String edgesPath = basePath + "/edges.txt";

            Console.WriteLine("saving files");
            CsvParserHelper.SaveTxt(clusterCentresPath, clusterCentres);
            CsvParserHelper.SaveTxt(codeVectorsPath, codeVectors, colDelimiter: ',');
            SaveTxt(nodeClusterIndexPath, nodeClusterIndex, 2);

            if (samples.Count < 1100000)
            {
                Console.WriteLine("Retrieving nearestnodes and edges");

                Console.WriteLine("Retrieving edges");
                List<float[]> edges = gh.GetEdges(codeVectors);
                int[,] edgeIndex = gh.GetEdgeIndex();

                List<GraphNode> nearestNodes = gh.GetNearestNeighbours(samples);
                Console.WriteLine("Retrieving dci");
                int[,] datapointClusterIndex = gh.GetDatapointClusterIndex(samples, nodeClusterIndex, nearestNodes);
                Console.WriteLine("Retrieving dni");
                int[,] datapointNodeIndex = gh.GetDatapointNodeIndex(samples, nearestNodes);
                SaveTxt(basePath + "/datapoint_cluster_index.txt", datapointClusterIndex, 2);
                SaveTxt(basePath + "/datapoint_node_index.txt", datapointNodeIndex, 2);
                SaveTxt(basePath + "/edge_index.txt", edgeIndex, 2);
                CsvParserHelper.SaveTxt(edgesPath, edges, colDelimiter: ',');
            }
            else
            {
                Console.WriteLine("Note creating dci dcn edges edge index because too many samples: {0}", samples.Count);
            }

            Console.WriteLine("Finished saving files");

        }

        public static void SaveTxt(String filePath, List<float[]> data, char colDelimiter = '\t', String lineDelimiter = "\r\n")
        {
            using (var sw = File.CreateText(filePath))
            //using (StreamWriter sw = new StreamWriter(filePath))
            {
                for (int i = 0; i < data.Count; i++)
                {
                    float[] line = data[i];
                    for (int j = 0; j < line.Length; j++)
                    {
                        sw.Write(line[j].ToString());
                        if (j < line.Length - 1)
                            sw.Write(colDelimiter);
                    }
                    sw.Write(lineDelimiter);
                }
            }
        }

        public static void SaveTxt(String filePath, int[,] data, int ndim, char colDelimiter = '\t', String lineDelimiter = "\r\n")
        {
            int numSamples = data.Length / ndim;

            using (var sw = File.CreateText(filePath))
            //using (StreamWriter sw = new StreamWriter(filePath))
            {
                for (int i = 0; i < numSamples; i++)
                {
                    for (int j = 0; j < ndim; j++)
                    {
                        sw.Write(data[i, j]);
                        if (j != ndim - 1)
                            sw.Write(colDelimiter);
                    }
                    sw.Write(lineDelimiter);
                }
            }
        }


        public List<SkyArea> LoadSkyAreas(String fileNameOrFolder)
        {
            var modelSkyAreas = new List<SkyArea>();

            if (Directory.Exists(fileNameOrFolder))
            {
                // if is a folder, then just process this folder
                SkyArea area = new SkyArea(0, 0);
                area.Path = fileNameOrFolder;
                modelSkyAreas.Add(area);
                return modelSkyAreas;
            }

            // is a file so load all the folders
            int id = 0;
            using (var sr = File.OpenText(fileNameOrFolder))
            {
                String line = null;
                while((line = sr.ReadLine()) != null)
                {
                    // first row is header
                    if (line.Equals("id,field,field_rect,sigma_rect"))
                        continue;
                    if (line.Length == 0) continue;
                    String[] vals = line.Split(new char[] { ',' });


                    int index = Int32.Parse(vals[0].Trim());
                    String indexPath = vals[1].Trim();
                    

                    SkyArea skyArea = new SkyArea(id, index);
                    skyArea.Path = indexPath;

                    modelSkyAreas.Add(skyArea);
                    id++;
                }
            }

            return modelSkyAreas;
        }

        public String GetSamplesFilePath(SkyArea skyArea)
        {
            if (this.MultipleSkyAreas)
                return this.BasePath + skyArea.Path + "/" + skyArea.Id + "/" + SamplesFileName;
            else
                return TestBasePath + "output_" + skyArea.Index + "/" + skyArea.Id + "/" + SamplesFileName;
        }

        public List<float[]> LoadSamples(List<SkyArea> modelSkyAreas)
        {
            ulong chunkSize = 500000;
            List<float[]> finalSamples = new List<float[]>();

            ulong totalAreaRows = 0;            
            foreach (SkyArea modelSkyArea in modelSkyAreas)
            {
                Console.WriteLine("Loading index: {0} skyarea: {1}  rows: {2}", modelSkyArea.Index, modelSkyArea.Id, modelSkyArea.NumSampleRows);

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

            if ((int) totalAreaRows != finalSamples.Count)
            {
                String err = String.Format("ERROR  ERROR Partial HDF5 read, read different number of records. {0} {1}", totalAreaRows, finalSamples.Count);
                Console.WriteLine(err);
                throw new Exception(err);

            }

            Console.WriteLine("Loaded " + finalSamples.Count + " samples -- totalRows: " + totalAreaRows);
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
            /*
            String samplesFilePath = GetSamplesFilePath(skyArea);
            float[,] data = HDF5Wrapper.LoadPartialHDF5(samplesFilePath, DataspaceName, offset, chunkSize, ndims, maxrows, maxcols);
            List<float[]> listData = ConvertToList(data, (int)ndims);
            return listData;
            */
            return null;
        }

        public ZScore PartialNormalization(int numDims, List<SkyArea> modelSkyAreas)
        {

            // normalization init
            double[] partial_mu = new double[numDims];
            List<double[]> partial_std = new List<double[]>();
            partial_std.Add(new double[numDims]);
            partial_std.Add(new double[numDims]);

            ulong numTotalSamples = 0;
            foreach (SkyArea skyArea in modelSkyAreas)
            {
                String samplesFilePath = GetSamplesFilePath(skyArea);
                ulong numRows = skyArea.NumSampleRows;
                ulong ndims = skyArea.NumSampleCols;

                ulong chunkSize = 100000;
                ulong i = 0;

                while (i < numRows)
                {
                    if (i + chunkSize >= numRows)
                        chunkSize = numRows - i;

                    List<float[]> listData = GetSamplesChunk(skyArea, i, chunkSize, ndims, skyArea.NumMaxRows, skyArea.NumMaxCols);

                    partial_mu = Normalize.PartialMean(listData, partial_mu);
                    partial_std = Normalize.PartialStandardDeviation(listData, partial_std);
                    
                    i += chunkSize;
                }

                numTotalSamples += skyArea.NumSampleRows;
            }

            ZScore z = new ZScore();
            z.Mu = Normalize.FinalizePartialMean((int)numDims, (int)numTotalSamples, partial_mu);
            z.Std = Normalize.FinalisePartialStandardDeviation(partial_std);
            SaveNorm(OutputPath, z);
            return z;
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


        public void SaveNorm(String filePath, ZScore z)
        {
            using (var sw = File.CreateText(filePath))
            //using (StreamWriter sw = new StreamWriter(filePath + "/mean.txt"))
            {
                StringBuilder sb = new StringBuilder();
                for(int i=0;i<z.Mu.Length;i++)
                {
                    sb.Append(z.Mu[i]);
                    if (i < z.Mu.Length - 1)
                        sb.Append(", ");
                }
                sw.WriteLine(sb);                
            }
            using (var sw = File.CreateText(filePath))
            //using (StreamWriter sw = new StreamWriter(filePath + "/std.txt"))
            {
                StringBuilder sb = new StringBuilder();
                for (int i = 0; i < z.Std.Length; i++)
                {
                    sb.Append(z.Std[i]);
                    if (i < z.Std.Length - 1)
                        sb.Append(", ");
                }
                sw.WriteLine(sb);
            }
        }

        public List<float[]> LogSamples(List<float[]> samples, bool handleNegatives = false)
        {
            if (handleNegatives)
                return LogSamples(samples);

            int numDims = samples[0].Length;

            for (int i = 0; i < samples.Count; i++)
            {
                float[] sample = samples[i];
                for (int j = 0; j < numDims; j++)
                {
                    if (sample[j] == 0)
                        sample[j] = 0.000001f;
                    float res = (float)Math.Log(sample[j]);
                    sample[j] = res;
                }
            }

            Console.WriteLine("Finished Logging: " + DateTime.Now);
            return samples;
        }

        public List<float[]> LogSamples(List<float[]> samples)
        {
            // log data
            //    min_sample_value = numpy.min(gen_samples[gen_samples > 0])
            //    gen_samples[gen_samples == 0] = (min_sample_value * 0.9)

            Console.WriteLine("Logging values");

            int numDims = samples[0].Length;

            float minValue = float.MaxValue;
            for (int i = 0; i < samples.Count; i++)
            {
                float[] sample = samples[i];
                for (int j = 0; j < numDims; j++)
                {
                    if (sample[j] < minValue && sample[j] != 0)
                        minValue = sample[j];
                }
            }

            // 10 percent less than smallest value
            minValue *= 0.9f;

            Console.WriteLine("Min value: " + minValue);

            int numLessThanZero = 0;

            for (int i = 0; i < samples.Count; i++)
            {
                float[] sample = samples[i];
                for (int j = 0; j < numDims; j++)
                {
                    if (sample[j] <= 0)
                    {
                        sample[j] = minValue;
                        numLessThanZero++;
                        //continue;
                    }
                    
                    sample[j] = (float) Math.Log(sample[j]);
                }
            }

            Console.WriteLine("Num less than zero: " + numLessThanZero);
            Console.WriteLine("Finished Logging");
            return samples;
        }

        public Dictionary<String, String[]> GetSampleFiles(List<SkyArea> skyAreas, String classification)
        {
            Dictionary<String, String[]> files = new Dictionary<String, String[]>();

            foreach (SkyArea skyArea in skyAreas)
            {                
                // get list of files.
                String samplePath = BasePath + skyArea.Path;
                String[] sampleDirectoryFolderPaths = Directory.GetDirectories(samplePath);

                foreach (String folderPath in sampleDirectoryFolderPaths)
                {
                    Console.WriteLine("Processing folder:{0}", folderPath);
                    if (folderPath.EndsWith("log"))
                    {
                        Console.WriteLine("skipping log folder");
                        continue;
                    }

                    String[] folderPathSections = folderPath.Split(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
                    String folderName = folderPathSections[folderPathSections.Length - 1];

                    String[] sampleDirectoryFilePaths = Directory.GetFiles(folderPath);
                    Regex rx = new Regex(@"(positions|samples).csv", RegexOptions.Compiled | RegexOptions.IgnoreCase);

                    foreach (String filePath in sampleDirectoryFilePaths)
                    {
                        String[] pathSections = filePath.Split(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
                        String fileName = pathSections[pathSections.Length - 1];

                        Match match = rx.Match(fileName, 0);
                        if (!match.Success)
                        {
                            Console.WriteLine("Skipping: {0}", fileName);
                            continue;
                        }

                        if (new FileInfo(filePath).Length == 0)
                        {
                            Console.WriteLine("File empty so skipping: {0}", filePath);
                            continue;
                        }

                        // positions or samples
                        String fileType = match.Groups[1].Value;

                        Console.WriteLine("Processing: {0}", fileName);

                        // add the file to the list
                        String key = skyArea.Id.ToString() + "-" + folderName;
                        if (!files.ContainsKey(key))
                            files.Add(key, new String[3]);

                        String[] region = files[key];
                        if (fileType == "positions")
                            region[0] = filePath;
                        if (fileType == "samples")
                            region[1] = filePath;

                        region[2] = "None";

                    }
                }
            }

            return files;
        }

        public Dictionary<String, String[]> GetSampleFiles2(List<SkyArea> skyAreas, String classification)
        {
            Dictionary<String, String[]> files = new Dictionary<String, String[]>();

            foreach (SkyArea skyArea in skyAreas)
            {
                // get list of files.
                String samplePath = skyArea.Path;
                String[] sampleDirectoryFilePaths = Directory.GetFiles(samplePath);
                
                Regex rx = new Regex(@"([0-9]+)-([0-9]+-[0-9]+-[0-9]+-[0-9]+)_(positions|samples).csv", RegexOptions.Compiled | RegexOptions.IgnoreCase);
                foreach (String filePath in sampleDirectoryFilePaths)
                {
                    String[] pathSections = filePath.Split(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
                    String fileName = pathSections[pathSections.Length - 1];
                    Match match = rx.Match(fileName, 0);
                    if (!match.Success)
                    {
                        Console.WriteLine("Skipping: {0}", fileName);
                        continue;
                    }

                    if (new FileInfo(filePath).Length == 0)
                    {
                        Console.WriteLine("File empty so skipping: {0}", filePath);
                        continue;
                    }                    

                    String classification_index = match.Groups[1].Value;
                    String imageRegion = match.Groups[2].Value;
                    String fileType = match.Groups[3].Value;

                    // if only want to process one classification then make sure we only add
                    // the files for that classification
                    // if classification length is zero then just process all the sample files.
                    if (classification.Length > 0 && !classification_index.Equals(classification))
                        continue;

                    Console.WriteLine("Processing: {0}", fileName);

                    // add the file to the list
                    String key = skyArea.Id + "_" + imageRegion;
                    if (!files.ContainsKey(key))
                        files.Add(key, new String[3]);

                    String[] region = files[key];
                    if (fileType == "positions")
                        region[0] = filePath;
                    if (fileType == "samples")
                        region[1] = filePath;

                    region[2] = classification_index;
                }

            }

            return files;
        }
    }
}
