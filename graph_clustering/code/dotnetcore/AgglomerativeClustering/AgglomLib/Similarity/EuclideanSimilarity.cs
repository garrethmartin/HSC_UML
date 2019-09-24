using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace AgglomerativeClustering
{
    class EuclideanSimilarity : Similarity
    {
        double Similarity.GetDistance(BiCluster one, BiCluster two)
        {
            double total = 0.0d;
            for (int k = 0; k < one.Vector.Length; k++)
            {
                float val = one.Vector[k] - two.Vector[k];
                total = total + (val * val);
            }
            return Math.Sqrt(total);
        }
    }
}
