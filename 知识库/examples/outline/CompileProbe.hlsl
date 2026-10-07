#include "OutlineMath.hlsl"

cbuffer Parameters : register(b0)
{
    float4x4 clipFromObject;
    float4x4 normalFromObject;
    float2 renderSize;
    float widthPixels;
    float minimumDepthScale;
};

struct VertexInput
{
    float3 positionOS : POSITION;
    float3 directionOS : NORMAL;
};

float4 OutlineVS(VertexInput input) : SV_Position
{
    float4 clipPosition = mul(clipFromObject, float4(input.positionOS, 1.0));
    // Test a supplied 2D direction; production projects construct pixelDirection
    // from their projection and normal-space convention before this call.
    float3 direction = mul((float3x3)normalFromObject, input.directionOS);
    return OffsetOutlinePixels(clipPosition, direction.xy, widthPixels, renderSize);
}

float4 OutlinePS(float4 positionCS : SV_Position) : SV_Target
{
    float edge = OutlineRelativeDepth(2.0, 2.1, minimumDepthScale);
    edge += OutlineNormalEdge(float3(0, 0, 1), float3(0, 1, 0));
    return float4(CompositeOutline(1.0.xxx, 0.0.xxx, edge), 1.0);
}
