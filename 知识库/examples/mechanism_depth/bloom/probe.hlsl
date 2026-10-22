Texture2D<float4> Source:register(t0);
SamplerState LinearClamp:register(s0);
float3 ExtractBloom(float3 color, float threshold, float knee)
{
    float brightness=max(color.r,max(color.g,color.b));
    if (brightness<=0.0) return float3(0,0,0);
    float soft=0.0;
    if (knee>0.0) {
        float q=clamp(brightness-threshold+knee,0.0,2.0*knee);
        soft=q*q/(4.0*knee);
    }
    float contribution=max(max(brightness-threshold,soft),0.0);
    return color*(contribution/brightness);
}

float3 TentUpsample(float2 uv, float2 sourceTexelSize)
{
    float3 result = 0;
    const float weights[3] = { 0.25, 0.5, 0.25 };
    for (int y=-1; y<=1; ++y)
        for (int x=-1; x<=1; ++x)
            result += weights[x+1]*weights[y+1]*
                Source.SampleLevel(LinearClamp,
                    uv+float2(x,y)*sourceTexelSize,0).rgb;
    return result;
}

float4 Probe(float2 uv:TEXCOORD0):SV_Target { return float4(TentUpsample(uv,float2(1.0/64,1.0/64))+ExtractBloom(float3(4,2,1),1,.5),1);}
