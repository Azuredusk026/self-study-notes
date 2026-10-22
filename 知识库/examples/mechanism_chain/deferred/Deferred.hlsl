// Direct3D conventions: UV top-left, depth [0,1], column-vector matrix math.
// View is rigid. All lighting directions/positions are in view space.
cbuffer Frame : register(b0) {
    float4x4 InvProjection;
    uint2 RenderSize;
    uint LightCount;
    uint TilesX;
};
struct GeometryInput {
    float4 position : SV_Position;
    float3 normalVS : TEXCOORD0;
    float4 baseMetal : TEXCOORD1;
    float4 emissiveRoughness : TEXCOORD2;
    nointerpolation uint model : TEXCOORD3;
};
struct GBufferOutput {
    float4 baseMetal : SV_Target0;       // RGBA8_UNORM, linear
    float4 normalRoughness : SV_Target1; // RGBA16_FLOAT
    float4 emissive : SV_Target2;        // RGBA16_FLOAT
    uint model : SV_Target3;             // R32_UINT, clear to 0xFFFFFFFF
};
GBufferOutput GBufferPS(GeometryInput input) {
    GBufferOutput o;
    o.baseMetal = input.baseMetal;
    o.normalRoughness = float4(normalize(input.normalVS)*0.5+0.5,
                              input.emissiveRoughness.w);
    o.emissive = float4(input.emissiveRoughness.xyz,0);
    o.model = input.model;
    return o;
}
Texture2D<float4> BaseMetal : register(t0);
Texture2D<float4> NormalRoughness : register(t1);
Texture2D<float4> Emissive : register(t2);
Texture2D<uint> Model : register(t3);
Texture2D<float> Depth : register(t4);
struct Light {
    float3 positionVS; float radius;
    float3 intensity; float unused;
};
StructuredBuffer<Light> Lights : register(t5);
StructuredBuffer<uint2> TileHeaders : register(t6);
StructuredBuffer<uint> LightIndices : register(t7);
RWTexture2D<float4> Output : register(u0);
float3 ReconstructPositionVS(float2 uv,float depth) {
    float4 h=mul(InvProjection,float4(uv.x*2-1,1-uv.y*2,depth,1));
    return h.xyz/h.w;
}
float G1(float c,float a2) { return 2*c/(c+sqrt(a2+(1-a2)*c*c)); }
float3 Response(float3 N,float3 V,float3 L,float3 base,float metal,float rough) {
    float nl=dot(N,L),nv=dot(N,V);
    if(nl<=0 || nv<=0) return 0;
    float3 H=normalize(V+L);
    float nh=saturate(dot(N,H)),vh=saturate(dot(V,H));
    float a=max(rough*rough,0.002),a2=a*a;
    float den=nh*nh*(a2-1)+1;
    float D=a2/(3.14159265359*den*den);
    float3 f0=lerp(0.04.xxx,base,metal);
    float3 F=f0+(1-f0)*pow(1-vh,5);
    return (1-F)*(1-metal)*base*nl/3.14159265359
           +D*G1(nl,a2)*G1(nv,a2)*F/(4*nv);
}
float3 PointContribution(float3 P,float3 N,float3 V,float4 bm,float rough,Light light) {
    float3 delta=light.positionVS-P;
    float d2=dot(delta,delta);
    if(d2>=light.radius*light.radius || d2<1e-12) return 0;
    float3 L=delta*rsqrt(d2);
    float fade=saturate(1-pow(d2/(light.radius*light.radius),2));
    float attenuation=fade*fade/max(d2,0.0001);
    return Response(N,V,L,bm.xyz,bm.w,rough)*light.intensity*attenuation;
}
[numthreads(8,8,1)]
void LightingCS(uint3 tid:SV_DispatchThreadID) {
    uint2 pixel=tid.xy;
    if(any(pixel>=RenderSize)) return;
    uint id=Model.Load(int3(pixel,0));
    if(id==0xFFFFFFFF) { Output[pixel]=float4(0,0,0,1); return; }
    float4 bm=BaseMetal.Load(int3(pixel,0));
    float3 color=Emissive.Load(int3(pixel,0)).xyz;
    if(id==1) { Output[pixel]=float4(bm.xyz+color,1); return; }
    if(id!=0) { Output[pixel]=float4(1,0,1,1); return; }
    float4 nr=NormalRoughness.Load(int3(pixel,0));
    float3 N=normalize(nr.xyz*2-1);
    float3 P=ReconstructPositionVS((pixel+0.5)/RenderSize,Depth.Load(int3(pixel,0)));
    float3 V=normalize(-P);
    uint2 tile=pixel/16;
    uint2 header=TileHeaders[tile.y*TilesX+tile.x];
    for(uint i=0;i<header.y;++i) {
        uint index=LightIndices[header.x+i];
        color+=PointContribution(P,N,V,bm,nr.w,Lights[index]);
    }
    Output[pixel]=float4(color,1);
}
