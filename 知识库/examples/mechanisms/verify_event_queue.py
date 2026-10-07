"""Compile and run the article's C# dispatch fragment with a minimal host."""
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ARTICLE = ROOT / '知识库/19_Gameplay与游戏框架/玩法事件与脚本.md'
BUILD = Path(__file__).parent / 'build/event-queue'


def verify():
    text = ARTICLE.read_text(encoding='utf-8')
    fragment = re.search(r'```csharp\n(.*?)\n```', text, re.S).group(1)
    BUILD.mkdir(parents=True, exist_ok=True)
    (BUILD / 'EventQueue.csproj').write_text('''<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType><TargetFramework>net10.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings><Nullable>enable</Nullable>
  </PropertyGroup>
</Project>
''', encoding='utf-8')
    harness = '''using System;
using System.Collections.Generic;
using System.Linq;

internal sealed class HandlerRegistry
{
    private Dictionary<Type, List<Action<object>>> m_handlers = new();

    internal IEnumerable<Action<object>> For(Type type)
    {
        if (m_handlers.TryGetValue(type, out var handlers))
        {
            return handlers;
        }
        return Enumerable.Empty<Action<object>>();
    }

    internal void Add<T>(Action<T> callback) where T : struct
    {
        if (!m_handlers.TryGetValue(typeof(T), out var callbacks))
        {
            callbacks = new List<Action<object>>();
            m_handlers.Add(typeof(T), callbacks);
        }
        callbacks.Add(message => callback((T)message));
    }
}

internal sealed class EventQueue
{
    internal HandlerRegistry handlers = new();
    internal int failures;
    private void LogHandlerFailure(Exception exception)
    {
        ++failures;
    }
FRAGMENT
}

internal static class Program
{
    private static void Require(bool condition)
    {
        if (!condition)
        {
            throw new InvalidOperationException("Event contract failed");
        }
    }

    private static void Main()
    {
        var queue = new EventQueue();
        var received = new List<int>();
        queue.handlers.Add<int>(value =>
        {
            received.Add(value);
            if (value == 1)
            {
                queue.Publish(2);
                queue.Flush();
            }
        });
        queue.Publish(1);
        queue.Flush();
        Require(received.SequenceEqual(new[] { 1 }));
        queue.Flush();
        Require(received.SequenceEqual(new[] { 1, 2 }));
        queue.handlers.Add<int>(value => throw new Exception("Expected failure"));
        int calls = 0;
        queue.handlers.Add<int>(value => ++calls);
        queue.Publish(3);
        queue.Flush();
        Require(queue.failures == 1 && calls == 1);
        Console.WriteLine("{\\"passed\\":true,\\"checks\\":3,\\"scope\\":\\"C# article fragment with mock handlers on .NET 10; no Unity runtime\\"}");
    }
}
'''.replace('FRAGMENT', fragment)
    (BUILD / 'Program.cs').write_text(harness, encoding='utf-8')
    result = subprocess.run(['dotnet', 'run', '--project', str(BUILD / 'EventQueue.csproj'),
                             '--configuration', 'Release', '--nologo'],
                            capture_output=True, text=True, encoding='utf-8')
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    record = json.loads(result.stdout.strip().splitlines()[-1])
    (BUILD / 'result.json').write_text(json.dumps(record, indent=2), encoding='utf-8')
    return record


if __name__ == '__main__':
    print(json.dumps(verify()))
