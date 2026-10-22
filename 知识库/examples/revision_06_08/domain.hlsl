struct ControlPoint { float3 position : POSITION; float3 normal : NORMAL; float2 uv : TEXCOORD0; };
struct PatchData { float outer[3] : SV_TessFactor; float inner : SV_InsideTessFactor; };
struct DomainOutput { float4 position : SV_Position; };
Texture2D<float> Height : register(t0);
SamplerState HeightSampler : register(s0);
cbuffer Parameters : register(b0) {
    row_major float4x4 WorldViewProjection;
    float Strength; float HeightBias; float HeightScale; float HeightMip;
};

float3 PhongPoint(float3 p0,float3 p1,float3 p2,
                  float3 n0,float3 n1,float3 n2,float3 bary,float strength) {
    float3 q=bary.x*p0+bary.y*p1+bary.z*p2;
    float3 a=q-dot(q-p0,n0)*n0;
    float3 b=q-dot(q-p1,n1)*n1;
    float3 c=q-dot(q-p2,n2)*n2;
    return lerp(q,bary.x*a+bary.y*b+bary.z*c,strength);
}

[domain("tri")]
DomainOutput DSMain(PatchData factors, float3 bary : SV_DomainLocation,
                    const OutputPatch<ControlPoint,3> points) {
    // Object-space control points, unit input normals, row-vector matrix.
    float3 position=PhongPoint(points[0].position,points[1].position,points[2].position,
        points[0].normal,points[1].normal,points[2].normal,bary,Strength);
    float3 normal=normalize(bary.x*points[0].normal+bary.y*points[1].normal+bary.z*points[2].normal);
    float2 uv=bary.x*points[0].uv+bary.y*points[1].uv+bary.z*points[2].uv;
    position+=normal*(Height.SampleLevel(HeightSampler,uv,HeightMip)-HeightBias)*HeightScale;
    DomainOutput output;
    output.position=mul(float4(position,1),WorldViewProjection);
    return output;
}
