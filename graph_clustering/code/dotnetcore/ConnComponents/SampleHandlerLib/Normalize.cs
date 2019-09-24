using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace SampleHandlerLib
{
    public class Normalize
    {
        public static List<float[]> MeanNormalizeData(List<float[]> samples)
        {
            float[] mu = Mean(samples);
            int ndim = samples[0].Length;
            List<float[]> meanNormalizedSamples = new List<float[]>();
            // subtract mean from each sample
            foreach (float[] sample in samples)
            {
                for (int i = 0; i < ndim; i++)
                {
                    sample[i] -= mu[i];
                }
                meanNormalizedSamples.Add(sample);
            }

            float[] new_mu = Mean(samples);
            for (int i = 0; i < new_mu.Length; i++)
            {
                Console.WriteLine("Feature Num: {0}  Old mu: {1}  New mu: {2}", i + 1, mu[i], new_mu[i]);
            }

            return meanNormalizedSamples;
        }


        public static List<double[]> NormalizeData(List<double[]> samples, double[] mu, double[] std)
        {
            int ndim = samples[0].Length;
            List<double[]> meanNormalizedSamples = new List<double[]>();
            // subtract mean from each sample
            foreach (double[] sample in samples)
            {
                for (int i = 0; i < ndim; i++)
                {
                    sample[i] -= mu[i];
                    //sample[i] /= std[i];
                    if (std[i] == 0)
                        sample[i] /= 1; //double.Epsilon;
                    else
                        sample[i] /= std[i];
                }
                meanNormalizedSamples.Add(sample);
            }

            double[] new_mu = Mean(samples);
            double[] new_std = StandardDeviation(samples);

            for (int i = 0; i < new_mu.Length; i++)
            {
                double mu_diff = Math.Abs(mu[i] - new_mu[i]);
                double std_diff = Math.Abs(std[i] - new_std[i]);
                Console.WriteLine("index/dim: {0}  mu diff: {1}  std diff: {2} new mu: {3}  new std: {4}", i, mu_diff, std_diff, new_mu[i], new_std[i]);
            }

            return meanNormalizedSamples;
        }


        public static List<float[]> NormalizeData(List<float[]> samples, float[] mu, float[] std)
        {

            int ndim = samples[0].Length;
            List<float[]> meanNormalizedSamples = new List<float[]>();
            // subtract mean from each sample
            foreach (float[] sample in samples)
            {
                for (int i = 0; i < ndim; i++)
                {
                    sample[i] -= mu[i];
                    //sample[i] /= std[i];
                    if (std[i] == 0)
                        sample[i] /= 1; //float.Epsilon;
                    else
                        sample[i] /= std[i];
                }
                meanNormalizedSamples.Add(sample);
            }

            float[] new_mu = Mean(samples);
            float[] new_std = StandardDeviation(samples);

            for (int i = 0; i < new_mu.Length; i++)
            {
                float mu_diff = Math.Abs(mu[i] - new_mu[i]);
                float std_diff = Math.Abs(std[i] - new_std[i]);
                Console.WriteLine("index/dim: {0}  mu diff: {1}  std diff: {2} new mu: {3}  new std: {4}", i, mu_diff, std_diff, new_mu[i], new_std[i]);
            }

            return meanNormalizedSamples;
        }

        public static List<float[]> NormalizeData(List<float[]> samples)
        {
            float[] mu = Mean(samples);
            float[] std = StandardDeviation(samples);

            return NormalizeData(samples, mu, std);
        }


        public static double[] PartialMean(List<float[]> samples, double[] intermediate_mu)
        {
            int ndim = samples[0].Length;

            // calc mean
            foreach (float[] sample in samples)
            {
                for (int i = 0; i < ndim; i++)
                    intermediate_mu[i] += sample[i];
            }

            return intermediate_mu;
        }

        public static float[] FinalizePartialMean(int ndim, int numTotalSamples, double[] inter_mu)
        {
            float[] mu = new float[ndim];
            for (int i = 0; i < ndim; i++)
                mu[i] = (float)inter_mu[i] / numTotalSamples;

            return mu;
        }

        public static double[] Mean(List<double[]> samples)
        {
            int ndim = samples[0].Length;
            double[] mu = new double[ndim];

            // calc mean
            foreach (double[] sample in samples)
            {
                for (int i = 0; i < ndim; i++)
                    mu[i] += sample[i];
            }

            double[] fmu = new double[ndim];
            for (int i = 0; i < ndim; i++)
                fmu[i] = (double)(mu[i] / samples.Count);

            return fmu;
        }

        public static float[] Mean(List<float[]> samples)
        {
            int ndim = samples[0].Length;
            double[] mu = new double[ndim];

            // calc mean
            foreach (float[] sample in samples)
            {
                for (int i = 0; i < ndim; i++)
                    mu[i] += sample[i];
            }

            float[] fmu = new float[ndim];
            for (int i = 0; i < ndim; i++)
                fmu[i] = (float)(mu[i] / samples.Count);

            return fmu;
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




        public static List<double[]> PartialStandardDeviation(List<float[]> valueList, List<double[]> partials)
        {
            int ndim = valueList[0].Length;
            int k = 1;

            double[] M = partials[0];
            double[] S = partials[1];
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

            partials[0] = M;
            partials[1] = S;
            return partials;
        }

        public static float[] FinalisePartialStandardDeviation(List<double[]> partials)
        {
            int ndim = partials[0].Length;

            double[] M = partials[0];
            double[] S = partials[1];
            int k = 1;
            float[] std = new float[ndim];
            for (int i = 0; i < ndim; i++)
            {
                //double t = 0.0001d;
                double variance = S[i] / (k - 2); // if whole population then k - 1
                //double dstd = Math.Sqrt(variance + t);
                double dstd = Math.Sqrt(variance);
                if (dstd > float.MaxValue)
                    Console.WriteLine("Larger than a float datatype");
                std[i] = (float)dstd; // warning reduces precision
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
                //double t = 0.0001d;
                double variance = S[i] / (k - 2); // if whole population then k - 1
                //double dstd = Math.Sqrt(variance + t);
                double dstd = Math.Sqrt(variance);
                if (dstd > float.MaxValue)
                    Console.WriteLine("Larger than a float datatype");
                std[i] = (float)dstd; // warning reduces precision
            }

            return std;
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

            /*
            double[] std = new double[ndim];
            for (int i = 0; i < ndim; i++)
            {
                std[i] = Math.Sqrt(S[i] / (k - 2)); // if whole population then k - 1
            }
            */

            double[] std = new double[ndim];
            for (int i = 0; i < ndim; i++)
            {
                //double t = 0.0001d;
                double variance = S[i] / (k - 2); // if whole population then k - 1
                //double dstd = Math.Sqrt(variance + t);
                double dstd = Math.Sqrt(variance);
                if (dstd > float.MaxValue)
                    Console.WriteLine("Larger than a float datatype");
                std[i] = (float)dstd; // warning reduces precision
            }
            return std;
        }

        public static List<double[]> LogDoubles(List<double[]> samples)
        {
            // log data
            //    min_sample_value = numpy.min(gen_samples[gen_samples > 0])
            //    gen_samples[gen_samples == 0] = (min_sample_value * 0.9)

            Console.WriteLine("Logging values");

            int numDims = samples[0].Length;

            double minValue = double.MaxValue;
            for (int i = 0; i < samples.Count; i++)
            {
                double[] sample = samples[i];
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
                double[] sample = samples[i];
                for (int j = 0; j < numDims; j++)
                {
                    if (sample[j] <= 0)
                    {
                        sample[j] = minValue;
                        numLessThanZero++;
                        //continue;
                    }

                    sample[j] = (double)Math.Log(sample[j]);
                }
            }

            Console.WriteLine("Num less than zero: " + numLessThanZero);
            Console.WriteLine("Finished Logging");
            return samples;
        }

        public static List<float[]> LogSamples(List<float[]> samples)
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

                    sample[j] = (float)Math.Log(sample[j]);
                }
            }

            Console.WriteLine("Num less than zero: " + numLessThanZero);
            Console.WriteLine("Finished Logging");
            return samples;
        }
    }
}
