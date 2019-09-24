using System;
using System.Collections.Generic;
using System.IO;
using CsvParser;
using Configuration;
using NumpyBinFiles;

namespace GNGConsoleApp
{
    class Program
    {
        static void Main(string[] args)
        {
            
            DateTime st = DateTime.Now;
            Console.WriteLine("Starting: {0}", st);

            Config config = Config.LoadConfig(args);

            InputOutputData io = new InputOutputData(config);
            io.Init();

            Process2(io, true);

            Console.WriteLine("Finishing: {0}", DateTime.Now);
            TimeSpan dur = (DateTime.Now - st);

            Console.WriteLine("Finished: {0}  Duration: {1}", DateTime.Now, dur);
        }

        public static Dictionary<String, String[]> Preprocess(Dictionary<String, String[]> files, InputOutputData io)
        {
            double[] intermediateMu = new double[20];
            var intermediateStd = new List<double[]>();
            bool init = false, normtest = true;
            int recLength = -1;
            int totalSamples = -1;

            if (io.Online)
            {
                intermediateMu = io.PartialMean;
                intermediateStd = io.PartialStd;
                totalSamples = io.TotalSamples;
                init = true;
            }
           
            
            var dedupeList = new HashSet<String>();
            Dictionary<String, List<int>> okIndices = new Dictionary<String, List<int>>();
            foreach(String key in files.Keys)
            {
                String[] region = files[key];

                String positionsFile = region[0];
                String samplesFile = region[1];
                List<float[]> samples = null;
                DateTime st = DateTime.Now;
                if (io.NPY) {
                    //List<float[]> samplesFile2 = CsvParserHelper.LoadFloats(samplesFile);
                    samplesFile = samplesFile.Replace(".csv", ".npy");
                    samples = Numpy.ReadFile(samplesFile);
                    //CompareData(samples, samplesFile2);
                }
                else
                    samples = CsvParserHelper.LoadFloats(samplesFile);

                recLength = samples[0].Length;

                if (!init)
                {
                    recLength = samples[0].Length;
                    intermediateMu = new double[recLength];
                    intermediateStd.Clear();
                    intermediateStd.Add(new double[recLength]);
                    intermediateStd.Add(new double[recLength]);
                    intermediateStd.Add(new double[recLength]);
                    init = true;
                }

                if (io.LogAllSamples)
                    samples = io.LogSamples(samples, false);
                
                // dedupe
                if (io.DeDupe)
                {
                    //List<int> indices = DeDupe.Dedupe(dedupeList, samples, io.DeDupePrecision);
                    //okIndices.Add(key, indices);
                }


                intermediateMu = Normalize.PartialMean(samples, intermediateMu);
                Console.WriteLine("Finished partial mean:" + DateTime.Now);
                intermediateStd = Normalize.PartialStandardDeviation(samples, intermediateStd);
                Console.WriteLine("Finished partial std:" + DateTime.Now);
                if (normtest)
                {
                    float[] tmu = Normalize.Mean(samples);
                    float[] tstd = Normalize.StandardDeviation(samples);

                    float[] sstd = Normalize.FinalisePartialStandardDeviation(intermediateStd);
                    float[] smu = Normalize.FinalizePartialMean(recLength, samples.Count, intermediateMu);
                    
                    Console.WriteLine("mu n {0} p {1}", String.Join(",", tmu), String.Join(",", smu));
                    Console.WriteLine("std n {0} p {1}", String.Join(",", tstd), String.Join(",", sstd));
                    normtest = false;

                }
                

                // calculate partial std and partial mean
                // dedupe?
                totalSamples += samples.Count;
                for (int i = 0; i < samples.Count; i++)
                    samples[i] = null;
                samples = null;
                Console.WriteLine("Finished cleanup: " + DateTime.Now);
            }


            CsvParserHelper.SaveTxt(io.OutputPath + "/partial_mean.csv", new List<double[]> { intermediateMu }, ',');
            CsvParserHelper.SaveTxt(io.OutputPath + "/partial_mean_sample_count.csv", new List<int[]> { new int[] { totalSamples }  }, ',');
            CsvParserHelper.SaveTxt(io.OutputPath + "/partial_std.csv", intermediateStd, ',');

            float[] std = Normalize.FinalisePartialStandardDeviation(intermediateStd);
            float[] mu = Normalize.FinalizePartialMean(recLength, totalSamples, intermediateMu);

            CsvParserHelper.SaveTxt(io.OutputPath + "/mean.csv", new List<float[]> { mu }, ',');
            CsvParserHelper.SaveTxt(io.OutputPath + "/std.csv", new List<float[]> { std }, ',');

            // save indicies
            /*int totalIndices = 0;
            io.OkIndicies = okIndices;
            foreach(String key in okIndices.Keys)
            {
                List<int> indices = okIndices[key];
                List<int[]> indicesOut = new List<int[]>();
                foreach (int index in indices)
                    indicesOut.Add(new int[] { index });
                totalIndices += indices.Count;
                CsvParserHelper.SaveTxt(io.ModelOutputPath + "/" + key + ".csv", indicesOut, ',');
            }
            */
            io.Mu = mu;
            io.Std = std;

            //Console.WriteLine("total recs: {0}  num ok indices: {1}", totalSamples, totalIndices);

            return files;
        }

        public static void Process2(InputOutputData io, bool preprocess=false)
        {
            
            Dictionary<String, String[]> files = io.GetSampleFiles(io.SkyAreas, io.Classification);

            if (preprocess)
                Preprocess(files, io);

            // load mu and std
            List<float[]> muList = CsvParserHelper.LoadFloats(io.OutputPath + "/mean.csv");
            List<float[]> stdList = CsvParserHelper.LoadFloats(io.OutputPath + "/std.csv");
            io.Mu = muList[0];
            io.Std = stdList[0];
            io.NumDimensions = io.Mu.Length;

            GNGRunner gr = new GNGRunner(io);


            int epochIter = 0;
            foreach (String[] inputFiles in files.Values)
            {
                DateTime st = DateTime.Now;
                String samplesFile = inputFiles[1];
                List<float[]> samples = null;                
                if (io.NPY)
                {
                    String npySamplesFilePath = samplesFile.Replace(".csv", ".npy");
                    samples = Numpy.ReadFile(npySamplesFilePath);
                    //samples = io.LoadSamples(modelSkyAreas);
                }
                else
                    samples = CsvParserHelper.LoadFloats(samplesFile);

                Console.WriteLine("Load file {0}  duration: {1}", samplesFile, DateTime.Now - st);


                if (io.LogAllSamples)
                    samples = io.LogSamples(samples, false);

                // normalize
                List<float[]> normedSamples = null;
                if (io.MeanAndUnitNormalize)
                    normedSamples = Normalize.NormalizeData(samples, io.Mu, io.Std);
                else
                    normedSamples = samples;

                int batchSize = io.BatchSize; // (samples.Count / 8) / 10; //12               
                gr.Train(samples, batchSize, epochIter);

                // clean up quickly.
                for (int i = 0; i < samples.Count; i++)
                    samples[i] = null;
                samples = null;

            }

            gr.SaveGNGModel();
            gr.SaveLog();
        }

    }

}
