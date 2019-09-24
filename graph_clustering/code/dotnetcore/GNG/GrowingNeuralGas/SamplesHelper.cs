using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.IO;
using CsvParser;

namespace GNG
{
    public class SamplesHelper
    {
        public static List<float[]> LoadSamples(String filePath)
        {
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
            return data;
        }

        public static void SaveTxt(String filePath, List<float[]> data, char colDelimiter = '\t', String lineDelimiter = "\r\n")
        {
            using (var sw = File.CreateText(filePath))
            //using (StreamWriter sw = new StreamWriter(filePath))
            {
                foreach (float[] line in data)
                {
                    foreach (float col in line)
                    {
                        sw.Write(col.ToString());
                        if (col != line[line.Length - 1])
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

        public static List<float[]> NormalizeData(List<float[]> samples)
        {
            float[] mu = Mean(samples);
            float[] std = StandardDeviation(samples);

            int ndim = samples[0].Length;
            List<float[]> meanNormalizedSamples = new List<float[]>();
            // subtract mean from each sample
            foreach (float[] sample in samples)
            {
                for (int i = 0; i < ndim; i++)
                {
                    sample[i] -= mu[i];
                    sample[i] /= std[i];
                }
                meanNormalizedSamples.Add(sample);
            }

            return meanNormalizedSamples;
        }

        public static float[] Mean(List<float[]> samples)
        {
            int ndim = samples[0].Length;
            float[] mu = new float[ndim];

            // calc mean
            foreach (float[] sample in samples)
            {
                for (int i = 0; i < ndim; i++)
                    mu[i] += sample[i];
            }

            for (int i = 0; i < ndim; i++)
                mu[i] /= samples.Count;

            return mu;
        }


        //http://stackoverflow.com/questions/895929/how-do-i-determine-the-standard-deviation-stddev-of-a-set-of-values
        public static double StandardDeviation(List<double> valueList)
        {
            double M = 0.0;
            double S = 0.0;
            int k = 1;
            foreach (double value in valueList)
            {
                double tmpM = M;
                M += (value - tmpM) / k;
                S += (value - tmpM) * (value - M);
                k++;
            }
            return Math.Sqrt(S / (k - 2));
        }

        public static double[] StandardDeviation(List<double[]> valueList)
        {
            int ndim = valueList[0].Length;

            double[] M = new double[ndim];
            double[] S = new double[ndim];
            int k = 1;
            foreach (double[] value in valueList)
            {
                for (int i = 0; i < ndim; i++)
                {
                    double tmpM = M[i];
                    M[i] += (value[i] - tmpM) / k;
                    S[i] += (value[i] - tmpM) * (value[i] - M[i]);
                }
                k++;
            }

            double[] std = new double[ndim];
            for (int i = 0; i < ndim; i++)
            {
                std[i] = Math.Sqrt(S[i] / (k - 2)); // if whole population then k - 1
            }

            return std;
        }


        public static float[] StandardDeviation(List<float[]> valueList)
        {
            int ndim = valueList[0].Length;

            double[] M = new double[ndim];
            double[] S = new double[ndim];
            int k = 1;
            foreach (float[] value in valueList)
            {
                for (int i = 0; i < ndim; i++)
                {
                    double tmpM = M[i];
                    M[i] += (value[i] - tmpM) / k;
                    S[i] += (value[i] - tmpM) * (value[i] - M[i]);
                }
                k++;
            }

            float[] std = new float[ndim];
            for (int i = 0; i < ndim; i++)
            {
                double dstd = Math.Sqrt(S[i] / (k - 2)); // if whole population then k - 1
                if (dstd > float.MaxValue)
                    Console.WriteLine("LArger than a float datatype");
                std[i] = (float)dstd; // warning reduces precision
            }

            return std;
        }
    }
}
