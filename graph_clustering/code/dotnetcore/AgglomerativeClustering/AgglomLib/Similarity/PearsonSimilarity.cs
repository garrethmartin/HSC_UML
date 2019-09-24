using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace AgglomerativeClustering
{
    public class PeasonSimilarity : Similarity
    {
        // fix for collective intelligence http://www.oreilly.com/catalog/errataunconfirmed.csp?isbn=9780596529321
        //http://stackoverflow.com/questions/13558529/pearson-algorithm-from-programming-collective-intelligence-still-not-working/13559801#13559801

        /*
        double Similarity.GetDistance(BiCluster one, BiCluster two)
        {
            // Collective Intelligence
            // pearson
            int numDims = one.Vector.Length; 
            double sum1 = one.Vector.Sum();
            double sum2 = two.Vector.Sum();

            double sum1sq = 0.0d;
            double sum2sq = 0.0d;
            double sumProd = 0.0d;
            for (int i = 0; i < numDims; i++)
            {
                sum1sq += (one.Vector[i] * one.Vector[i]);
                sum2sq += (two.Vector[i] * two.Vector[i]);
                sumProd += (one.Vector[i] * two.Vector[i]);
            }
            
            // calc pearson score
            double num = sumProd - (sum1 * sum2 / numDims);
            double den = Math.Sqrt((sum1sq - Math.Pow(sum1, 2) / numDims) * (sum2sq - Math.Pow(sum2, 2) / numDims));
            if (den == 0)
                return 0;
            else
                return 1.0-num/den;
        }
        */
        double Similarity.GetDistance(BiCluster one, BiCluster two)
        {
            // https://code.google.com/p/sprwikiwordrelatedness/source/browse/trunk/src/main/java/edu/osu/slate/experiments/Pearson.java?r=62
            float[] xVect = one.Vector;
            float[] yVect = two.Vector;

            double meanX = 0.0, meanY = 0.0;
            for (int i = 0; i < xVect.Length; i++)
            {
                meanX += xVect[i];
                meanY += yVect[i];
            }

            meanX /= xVect.Length;
            meanY /= yVect.Length;

            double sumXY = 0.0, sumX2 = 0.0, sumY2 = 0.0;
            for (int i = 0; i < xVect.Length; i++)
            {
                sumXY += ((xVect[i] - meanX) * (yVect[i] - meanY));
                sumX2 += Math.Pow(xVect[i] - meanX, 2.0);
                sumY2 += Math.Pow(yVect[i] - meanY, 2.0);
            }

            return 1 - (sumXY / (Math.Sqrt(sumX2) * Math.Sqrt(sumY2)));

        }
    }
}

