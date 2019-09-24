using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using System.IO;


namespace Configuration
{
    public class Config : Dictionary<String, String>
    {
        private String path = null;
        private String basePath = null;

        public Config() { }

        public Config(String path) { this.path = path; }

        public Config(String path, String basePath)
        {
            this.path = path;
            this.basePath = basePath;
        }

        public int Int(String key)
        {
            if (!ValidateKey(key))
                return -1;

            try
            {
                return Int32.Parse(this[key]);
            }
            catch (FormatException ex)
            {
                Console.WriteLine("Could not parse int value: {0} {1} ", key, this[key]);
                throw ex;
            }
        }

        public int[] Ints(String key)
        {
            if (!ValidateKey(key))
                return new int[1] { -1 };

            try
            {
                String temp = this[key];
                String[] temps = temp.Split(new char[] { ',' }, StringSplitOptions.RemoveEmptyEntries);
                int[] result = new int[temps.Length];
                for (int i = 0; i < temps.Length; i++)
                    result[i] = Int32.Parse(temps[i]);
                return result;
            }
            catch (FormatException ex)
            {
                Console.WriteLine("Could not parse int value: {0} {1} ", key, this[key]);
                throw ex;
            }
        }

        public String[] Strings(String key)
        {
            if (!ValidateKey(key))
                return new String[1] { "Error" };

            try
            {
                String temp = this[key];
                String[] result = temp.Split(new char[] { ',' }, StringSplitOptions.RemoveEmptyEntries);
                return result;
            }
            catch (FormatException ex)
            {
                Console.WriteLine("Could not parse int value: {0} {1} ", key, this[key]);
                throw ex;
            }
        }
        public float Float(String key)
        {
            if (!ValidateKey(key))
                return -1.0f;

            try
            {
                return float.Parse(this[key]);
            }
            catch (FormatException ex)
            {
                Console.WriteLine("Could not parse float value: {0}, {1}", key, this[key]);
                throw ex;
            }
        }

        public double Double(String key)
        {
            if (!ValidateKey(key))
                return -1.0d;

            try
            {
                return double.Parse(this[key]);
            }
            catch (FormatException ex)
            {
                Console.WriteLine("Could not parse double value: {0}, {1}", key, this[key]);
                throw ex;
            }
        }

        public string Get(String key)
        {
            if (!ValidateKey(key))
                return null;

            return this[key];
        }

        public bool Bool(String key)
        {
            String val = "";
            try
            {
                val = this[key].ToLower();
            }
            catch (Exception ex)
            {
                Console.WriteLine("Key doesn't exist {0}", key);
                throw new Exception("Key doesn't exist: " + key, ex);
            }

            if (val == "true" || val == "y" || val == "yes")
                return true;
            else
                return false;

        }

        public bool ValidateKey(String key)
        {
            if (ContainsKey(key))
                return true;

            Console.WriteLine("Key doesn't exist: {0}", key);
            return false;
        }

        public void Reload()
        {
            Reload(true);
        }

        public void Reload(bool withClear)
        {
            if (withClear)
                this.Clear();

            if (this.basePath != null)
                this.Add("BASEPATH", basePath);

            foreach (var row in File.ReadAllLines(this.path))
            {
                if (row.Trim().Length == 0)
                    continue;
                if (row.Trim().StartsWith("#"))
                    continue;
                string key = row.Split('=')[0];
                int idx = row.IndexOf('=');
                string val = row.Substring(idx + 1);
                Console.WriteLine("{0}={1}", key, val);
                Add(key, val);
            }

            List<String> keys = this.Keys.ToList();

            foreach (String key in keys)
            {
                String value = this[key];
                int startIndex = value.IndexOf("<<");
                int endIndex = value.IndexOf(">>");
                if (startIndex == -1 && endIndex == -1)
                    continue;
                if (startIndex > -1 && endIndex == -1)
                {
                    Console.WriteLine("Error << but no >> in {0}", key);
                    continue;
                }
                if (startIndex == -1 && endIndex > -1)
                {
                    Console.WriteLine("Error >> but no << in {0}", key);
                    continue;
                }

                String embeddedKey = value.Substring(startIndex + 2, endIndex - startIndex - 2);
                if (!this.ContainsKey(embeddedKey))
                {
                    Console.WriteLine("Error embedded key does not exist: {0}", embeddedKey);
                    continue;
                }

                // replace macro
                value = value.Replace("<<" + embeddedKey + ">>", this[embeddedKey]);
                this[key] = value;

                Console.WriteLine("Updated Key: {0}={1}", key, value);
            }

            Console.WriteLine("Loaded {0} properties", this.Keys.Count);
        }

        public static Config LoadConfig(String[] args)
        {
            String configPath = args[0];
            Console.WriteLine("Loading config file: {0}", configPath);

            var options = new Config(configPath);

            if (args.Length > 1) // parse command line arguments first
            {
                String lastKey = null;
                for (int i = 1; i < args.Length; i++)
                {
                    String option = args[i].Trim();
                    String key = null;
                    if (lastKey == null && option.StartsWith("--"))
                    {
                        key = option.Replace("--", "");
                    }
                    if (lastKey != null && option.StartsWith("--"))
                        throw new Exception(String.Format("two options in a row: {0} {1}, {1}", lastKey, option, args));

                    if (lastKey != null)
                    {
                        options[lastKey] = option;
                        lastKey = null;
                    }
                    else
                        lastKey = key;
                }
            }

            // load config file and update all embedded keys
            options.Reload(false);
            return options;
        }

        public static Config LoadConfig(String configPath, String basePath)
        {
            Console.WriteLine("Loading config file: {0} using basePath: {1} ", configPath, basePath);
            var config = new Config(configPath, basePath);
            config.Reload();
            return config;
        }
    }

}
