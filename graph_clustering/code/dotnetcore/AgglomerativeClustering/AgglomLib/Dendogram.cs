using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
//using System.Drawing;
//using System.Drawing.Imaging;
using System.IO;

namespace AgglomerativeClustering
{
    public class Dendogram
    {
        public Dendogram() { }

        public int GetHeight(BiCluster cluster)
        {
            // is this an endpoint, then the height is just one
            if (cluster.Left == null && cluster.Right == null)
                return 1;

            // otherwise the height is the same of the heights of each branch
            return GetHeight(cluster.Left) + GetHeight(cluster.Right);
        }

        public float GetDepth(BiCluster cluster)
        {
            // the distance of an endpoint is 0.0
            if (cluster.Left == null && cluster.Right == null)
                return 0;

            // the distance of a branch is the greater of its two sides plus its own distance
            return Math.Max(GetDepth(cluster.Left), GetDepth(cluster.Right)) + (float) cluster.Distance;
        }
        /*
        public void DrawDendogram(BiCluster cluster, List<String> labels, String filePath = "clusters.jpg")
        {
            int height = GetHeight(cluster) * 20;
            int width = 1200;
            float depth = GetDepth(cluster);

            // width is fixed so scale distances accordingly
            float scaling = (width - 150) / depth;

            try
            {

                // create a new image with a white background
                using (var bitmap = new Bitmap(width, height))
                {
                    using (Graphics g = Graphics.FromImage(bitmap))
                    {
                        // Make the background white
                        Rectangle rect = new Rectangle(0, 0, width, height);
                        g.FillRectangle(new SolidBrush(Color.White), rect);

                        g.DrawLine(new Pen(Color.Black), 0, height / 2, 10, height / 2);

                        // draw the first node
                        DrawNode(g, cluster, 10, (height / 2), scaling, labels);
                    }
                    // save the image
                    bitmap.Save(filePath, ImageFormat.Jpeg);
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.ToString());
            }
        }

        public void DrawNode(Graphics g, BiCluster cluster, float x, float y, float scaling, List<String> labels)
        {
            if (cluster.Id < 0)
            {
                Pen blackPen = new Pen(Color.Black);

                int h1 = GetHeight(cluster.Left) * 20;
                int h2 = GetHeight(cluster.Right) * 20;
                float top = y - (h1 + h2) / 2;
                float bottom = y + (h1 + h2) / 2;

                // line length
                float lineLength = (float)cluster.Distance * scaling;
                // vertical line from this cluster to its children
                g.DrawLine(blackPen, x, top + h1 / 2, x, bottom - h2 / 2);

                // horizontal line to left item
                g.DrawLine(blackPen, x, top + h1 / 2, x + lineLength, top + h1 / 2);

                // horizontal line to right item
                g.DrawLine(blackPen, x, bottom - h2 / 2, x + lineLength, bottom - h2 / 2);                

                // recurse
                DrawNode(g, cluster.Left, x + lineLength, top + h1 / 2, scaling, labels);
                DrawNode(g, cluster.Right, x + lineLength, bottom - h2 / 2, scaling, labels);

                //Font drawFont = new Font("Arial", 16);
                //SolidBrush drawBrush = new SolidBrush(Color.Black);
                //g.DrawString(cluster.Id.ToString(), drawFont, drawBrush, x - 20, y + 3);
            }

        }
        */
    }
}
