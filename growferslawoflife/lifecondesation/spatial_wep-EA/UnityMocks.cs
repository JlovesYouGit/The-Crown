namespace UnityEngine
{
    public struct Vector3
    {
        public float x, y, z;
        public Vector3(float x, float y, float z) { this.x = x; this.y = y; this.z = z; }
        public static float Dot(Vector3 a, Vector3 b) => a.x * b.x + a.y * b.y + a.z * b.z;
        public static Vector3 zero => new Vector3(0, 0, 0);
        public float magnitude => (float)Math.Sqrt(x * x + y * y + z * z);
        public Vector3 normalized { get { float m = magnitude; return m > 0 ? new Vector3(x / m, y / m, z / m) : zero; } }
        public static float Distance(Vector3 a, Vector3 b) => (new Vector3(a.x - b.x, a.y - b.y, a.z - b.z)).magnitude;
        public float sqrMagnitude => x * x + y * y + z * z;

        public static Vector3 operator -(Vector3 a, Vector3 b) => new Vector3(a.x - b.x, a.y - b.y, a.z - b.z);
        public static Vector3 operator +(Vector3 a, Vector3 b) => new Vector3(a.x + b.x, a.y + b.y, a.z + b.z);
        public static Vector3 operator *(Vector3 a, float d) => new Vector3(a.x * d, a.y * d, a.z * d);

        public override string ToString() => $"({x:F2}, {y:F2}, {z:F2})";
    }

    public static class Mathf
    {
        public const float PI = (float)Math.PI;
        public static float Abs(float f) => Math.Abs(f);
        public static float Pow(float f, float p) => (float)Math.Pow(f, p);
        public static float Max(float a, float b) => Math.Max(a, b);
        public static float Min(float a, float b) => Math.Min(a, b);
        public static float Clamp01(float value) => Math.Max(0, Math.Min(1, value));
    }

    public static class Debug
    {
        public static void Log(object m) => Console.WriteLine($"[LOG] {m}");
        public static void LogWarning(object m) => Console.WriteLine($"[WARN] {m}");
        public static void LogError(object m) => Console.WriteLine($"[ERR] {m}");
    }

    public class MonoBehaviour
    {
        public T GetComponent<T>() where T : MonoBehaviour => Simulator.Instance.GetComponent<T>(this);
        public void StartCoroutine(System.Collections.IEnumerator routine) => Simulator.Instance.StartCoroutine(routine);
    }

    public class WaitForSeconds
    {
        public float Seconds;
        public WaitForSeconds(float seconds) => Seconds = seconds;
    }

    public static class Time
    {
        public static float deltaTime = 0.016f; // Simulation step
    }

    [AttributeUsage(AttributeTargets.Field)]
    public class HeaderAttribute : Attribute { public HeaderAttribute(string s) {} }

    public class Simulator
    {
        public static Simulator Instance = new Simulator();
        private Dictionary<Type, MonoBehaviour> _components = new Dictionary<Type, MonoBehaviour>();
        private List<System.Collections.IEnumerator> _coroutines = new List<System.Collections.IEnumerator>();
        private bool _started = false;

        public T AddComponent<T>() where T : MonoBehaviour, new()
        {
            var comp = new T();
            _components[typeof(T)] = comp;
            
            // Call Awake
            var awake = typeof(T).GetMethod("Awake", System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.NonPublic);
            awake?.Invoke(comp, null);
            
            return comp;
        }

        public T GetComponent<T>(MonoBehaviour caller) where T : MonoBehaviour
        {
            if (_components.TryGetValue(typeof(T), out var comp)) return (T)comp;
            return null;
        }

        public void StartCoroutine(System.Collections.IEnumerator routine) => _coroutines.Add(routine);

        public void RunSimulation(int steps)
        {
            Console.WriteLine("--- SIMULATION START ---");
            
            // Call Start on all components
            if (!_started)
            {
                foreach (var comp in _components.Values)
                {
                    var start = comp.GetType().GetMethod("Start", System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.NonPublic);
                    start?.Invoke(comp, null);
                }
                _started = true;
            }

            for (int i = 0; i < steps; i++)
            {
                foreach (var comp in _components.Values)
                {
                    var updateTarget = comp.GetType().GetMethod("Update", System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.NonPublic);
                    updateTarget?.Invoke(comp, null);
                }

                for (int j = _coroutines.Count - 1; j >= 0; j--)
                {
                    if (!_coroutines[j].MoveNext()) _coroutines.RemoveAt(j);
                }
            }
            Console.WriteLine("--- SIMULATION END ---");
        }
    }
}


