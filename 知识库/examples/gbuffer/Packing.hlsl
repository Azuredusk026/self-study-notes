float2 SignNotZero(float2 value)
{
    return float2(value.x >= 0.0 ? 1.0 : -1.0,
                  value.y >= 0.0 ? 1.0 : -1.0);
}

float2 EncodeNormal(float3 normal)
{
    normal /= abs(normal.x) + abs(normal.y) + abs(normal.z);
    float2 encoded = normal.xy;
    if (normal.z < 0.0)
        encoded = (1.0 - abs(encoded.yx)) * SignNotZero(encoded);
    return encoded * 0.5 + 0.5;
}

float3 DecodeNormal(float2 packed)
{
    float2 f = packed * 2.0 - 1.0;
    float3 normal = float3(f, 1.0 - abs(f.x) - abs(f.y));
    float correction = saturate(-normal.z);
    normal.xy -= SignNotZero(normal.xy) * correction;
    return normalize(normal);
}

float PackFloat5UInt3(float value, uint identifier)
{
    uint quantized = (uint)floor(saturate(value) * 31.0 + 0.5);
    uint byteValue = (identifier & 7u) * 32u + quantized;
    return byteValue / 255.0;
}

uint UnpackIdentifier(float packed)
{
    uint byteValue = (uint)floor(saturate(packed) * 255.0 + 0.5);
    return byteValue / 32u;
}

float UnpackValue(float packed)
{
    uint byteValue = (uint)floor(saturate(packed) * 255.0 + 0.5);
    return (byteValue % 32u) / 31.0;
}

float4 ProbePS(float4 position : SV_Position) : SV_Target
{
    float3 normal = DecodeNormal(EncodeNormal(normalize(float3(1, -2, 3))));
    float packed = PackFloat5UInt3(normal.x * 0.5 + 0.5, 5u);
    return float4(normal, UnpackValue(packed) + UnpackIdentifier(packed));
}
