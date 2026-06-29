

# Grok 4.3
<a name="model-card-xai-grok-4-3"></a>

## ![Icon showing the xAI logo.](http://docs.aws.amazon.com/bedrock/latest/userguide/images/models/xai.png) xAI — Grok 4.3
<a name="model-card-xai-grok-4-3-header"></a>

## Model Details
<a name="model-card-xai-grok-4-3-details"></a>

Grok 4.3 is a reasoning-first model that offers always-on and configurable reasoning effort (none, low, medium, high). Because reasoning is always active rather than optional, it behaves more consistently across multi-step agent loops than models that can skip thinking. It also offers strong tool use and instruction-following capabilities for building multi-step agents, and token efficiency to help keep high-volume inference cost-effective. Grok 4.3 is especially well suited to enterprise workloads such as contract review, case law research, credit agreement analysis, and financial document Q&A, while delivering consistent, high-quality results across conversational AI, search, chat, and multi-turn workflows. Grok 4.3 runs on Mantle, a new inference engine in Amazon Bedrock designed for price performance, with support for tool calling, structured output, and response streaming.
+ **Model launch date:** June 15, 2026
+ **Model EOL date:** N/A
+ **End User License Agreements and Terms of Use:** [View](https://aws.amazon.com/legal/bedrock/third-party-models/)
+ **Model lifecycle:** Active
+ **Context window:** 1M tokens
+ **Reasoning:** Supported (configurable: low, medium, high)


| **Input Modalities** | **Output Modalities** | **[APIs supported](https://docs.aws.amazon.com/bedrock/latest/userguide/apis.html)** | **[Endpoints supported](https://docs.aws.amazon.com/bedrock/latest/userguide/endpoints.html)** | 
| --- | --- | --- | --- | 
| ![Red circle with white X icon indicating error, cancel, or close action.](http://docs.aws.amazon.com/bedrock/latest/userguide/images/icons/icon-no.png) Audio | ![Red circle with white X icon indicating error, cancel, or close action.](http://docs.aws.amazon.com/bedrock/latest/userguide/images/icons/icon-no.png) Embedding | ![Green circle with white checkmark icon.](http://docs.aws.amazon.com/bedrock/latest/userguide/images/icons/icon-yes.png) Chat Completions | ![Red circle with white X icon indicating error, cancel, or close action.](http://docs.aws.amazon.com/bedrock/latest/userguide/images/icons/icon-no.png) bedrock-runtime | 
| ![Green circle with white checkmark icon.](http://docs.aws.amazon.com/bedrock/latest/userguide/images/icons/icon-yes.png) Image | ![Red circle with white X icon indicating error, cancel, or close action.](http://docs.aws.amazon.com/bedrock/latest/userguide/images/icons/icon-no.png) Image | ![Green circle with white checkmark icon.](http://docs.aws.amazon.com/bedrock/latest/userguide/images/icons/icon-yes.png) Responses | ![Green circle with white checkmark icon.](http://docs.aws.amazon.com/bedrock/latest/userguide/images/icons/icon-yes.png) bedrock-mantle | 
| ![Red circle with white X icon indicating error, cancel, or close action.](http://docs.aws.amazon.com/bedrock/latest/userguide/images/icons/icon-no.png) Speech | ![Red circle with white X icon indicating error, cancel, or close action.](http://docs.aws.amazon.com/bedrock/latest/userguide/images/icons/icon-no.png) Speech | ![Red circle with white X icon indicating error, cancel, or close action.](http://docs.aws.amazon.com/bedrock/latest/userguide/images/icons/icon-no.png) Invoke |  | 
| ![Green circle with white checkmark icon.](http://docs.aws.amazon.com/bedrock/latest/userguide/images/icons/icon-yes.png) Text | ![Green circle with white checkmark icon.](http://docs.aws.amazon.com/bedrock/latest/userguide/images/icons/icon-yes.png) Text | ![Red circle with white X icon indicating error, cancel, or close action.](http://docs.aws.amazon.com/bedrock/latest/userguide/images/icons/icon-no.png) Converse |  | 
| ![Red circle with white X icon indicating error, cancel, or close action.](http://docs.aws.amazon.com/bedrock/latest/userguide/images/icons/icon-no.png) Video | ![Red circle with white X icon indicating error, cancel, or close action.](http://docs.aws.amazon.com/bedrock/latest/userguide/images/icons/icon-no.png) Video |  |  | 

**Note**  
This model is available on the `openai/v1/responses` path on the `bedrock-mantle` endpoint. This is different from the `v1/responses` path used by other models on the responses endpoint.

## Capabilities and Features
<a name="model-card-xai-grok-4-3-capabilities"></a>

***Bedrock Features***

**Features supported using `bedrock-mantle` endpoint**


| **Supported** | **Not Supported** | 
| --- | --- | 
|  [See the AWS documentation website for more details](http://docs.aws.amazon.com/bedrock/latest/userguide/model-card-xai-grok-4-3.html)  | — | 

## Pricing
<a name="model-card-xai-grok-4-3-pricing"></a>

For pricing, please refer to the [Amazon Bedrock Pricing](https://aws.amazon.com/bedrock/pricing/) page.

## Programmatic Access
<a name="model-card-xai-grok-4-3-programmatic-access"></a>

Use the following model IDs and endpoint URLs to access this model programmatically. For more information about the available APIs and endpoints, see [APIs supported](https://docs.aws.amazon.com/bedrock/latest/userguide/apis.html) and [Endpoints supported](https://docs.aws.amazon.com/bedrock/latest/userguide/endpoints.html).


| **Endpoint** | **Model ID** | **In-Region endpoint URL** | **Geo inference ID** | **Global inference ID** | 
| --- | --- | --- | --- | --- | 
| bedrock-mantle | xai.grok-4.3 | https://bedrock-mantle.{region}.api.aws/openai/v1 | Not supported | Not supported | 

*For example, if region is us-west-2 (Oregon), then the bedrock-mantle endpoint URL will be "https://bedrock-mantle.us-west-2.api.aws/openai/v1".*

## Service Tiers
<a name="model-card-xai-grok-4-3-tiers"></a>

Amazon Bedrock offers multiple service tiers to match your workload requirements. **Standard** provides pay-per-token access with no commitment. **Priority** offers higher throughput with a time-based commitment. **Flex** provides lower-cost access for flexible, non-time-sensitive workloads. **Reserved** provides dedicated throughput with a term commitment for predictable workloads. For more information, see [service tiers](https://docs.aws.amazon.com/bedrock/latest/userguide/service-tiers-inference.html).


| **Standard** | **Priority** | **Flex** | **Reserved** | 
| --- | --- | --- | --- | 
| ![Green circle with white checkmark icon.](http://docs.aws.amazon.com/bedrock/latest/userguide/images/icons/icon-yes.png) | ![Green circle with white checkmark icon.](http://docs.aws.amazon.com/bedrock/latest/userguide/images/icons/icon-yes.png) | ![Green circle with white checkmark icon.](http://docs.aws.amazon.com/bedrock/latest/userguide/images/icons/icon-yes.png) | ![Red circle with white X icon indicating error, cancel, or close action.](http://docs.aws.amazon.com/bedrock/latest/userguide/images/icons/icon-no.png) | 

## Regional Availability
<a name="model-card-xai-grok-4-3-regional-availability"></a>

***Regional availability at a glance***

Bedrock offers three inference options: **In-Region** keeps requests within a single Region for strict compliance, **Geo Cross-Region** routes across Regions within a geography (US, EU, etc.) for higher throughput while respecting data residency, and **Global Cross-Region** routes anywhere worldwide for maximum throughput when there are no residency constraints. Refer to the [Regional availability by models](models-region-compatibility.md) page for more details.


| **Region** | **In-Region** | **Geo** | **Global** | 
| --- | --- | --- | --- | 
| us-west-2 (Oregon) | ![Green circle with white checkmark icon.](http://docs.aws.amazon.com/bedrock/latest/userguide/images/icons/icon-yes.png) | ![Red circle with white X icon indicating error, cancel, or close action.](http://docs.aws.amazon.com/bedrock/latest/userguide/images/icons/icon-no.png) | ![Red circle with white X icon indicating error, cancel, or close action.](http://docs.aws.amazon.com/bedrock/latest/userguide/images/icons/icon-no.png) | 
| us-east-1 (N. Virginia) | ![Green circle with white checkmark icon.](http://docs.aws.amazon.com/bedrock/latest/userguide/images/icons/icon-yes.png) | ![Red circle with white X icon indicating error, cancel, or close action.](http://docs.aws.amazon.com/bedrock/latest/userguide/images/icons/icon-no.png) | ![Red circle with white X icon indicating error, cancel, or close action.](http://docs.aws.amazon.com/bedrock/latest/userguide/images/icons/icon-no.png) | 
| us-east-2 (Ohio) | ![Green circle with white checkmark icon.](http://docs.aws.amazon.com/bedrock/latest/userguide/images/icons/icon-yes.png) | ![Red circle with white X icon indicating error, cancel, or close action.](http://docs.aws.amazon.com/bedrock/latest/userguide/images/icons/icon-no.png) | ![Red circle with white X icon indicating error, cancel, or close action.](http://docs.aws.amazon.com/bedrock/latest/userguide/images/icons/icon-no.png) | 

## Quotas and Limits
<a name="model-card-xai-grok-4-3-quotas"></a>

Your AWS account has default quotas to maintain the performance of the service and to ensure appropriate usage of Amazon Bedrock. The default quotas assigned to an account might be updated depending on regional factors, payment history, fraudulent usage, and/or approval of a quota [increase request](https://docs.aws.amazon.com/bedrock/latest/userguide/quotas-increase.html). For more details, please refer to [Quotas for Amazon Bedrock](quotas.md) documentation and see the [limits](https://docs.aws.amazon.com/general/latest/gr/bedrock.html#limits_bedrock) for the model.

When consuming on-demand throughput on the `bedrock-mantle` endpoint, [available throughput scales over time](https://docs.aws.amazon.com/bedrock/latest/userguide/scaling-throughput-best-practices.html#scaling-ramp-up). Not all requests within your quota are guaranteed to succeed during periods of high demand, so ramping gradually is important. For this model, default limits aren't surfaced directly through Service Quotas, so we recommend following the ramp as your guide.

## Sample Code
<a name="model-card-xai-grok-4-3-sample-code"></a>

**Step 1 - AWS Account:** If you have an AWS account already, skip this step. If you are new to AWS, sign up for an [AWS account](https://portal.aws.amazon.com/billing/signup).

**Step 2 - API key:** Go to the [Amazon Bedrock console](https://console.aws.amazon.com/bedrock/home#/api-keys/long-term/create) and generate a long-term API key.

**Step 3 - Get the SDK:** To use this getting started guide, you must have Python already installed. Then install the relevant software depending on the APIs you are using.

------
#### [ Chat Completions API ]

```
pip install openai
```

------
#### [ Responses API ]

```
pip install openai
```

------

**Step 4 - Set environment variables:** Configure your environment to use the API key for authentication.

------
#### [ Chat Completions API ]

```
OPENAI_API_KEY="<provide your Bedrock API key>"
OPENAI_BASE_URL="https://bedrock-mantle.us-west-2.api.aws/openai/v1"
```

------
#### [ Responses API ]

```
OPENAI_API_KEY="<provide your Bedrock API key>"
OPENAI_BASE_URL="https://bedrock-mantle.us-west-2.api.aws/openai/v1"
```

------

**Step 5 - Run your first inference request:** Save the file as `bedrock-first-request.py`

------
#### [ Chat Completions API ]

```
from openai import OpenAI

client = OpenAI()

response = client.chat.completions.create(
    model="xai.grok-4.3",
    messages=[
        {"role": "user", "content": "Can you explain the features of Amazon Bedrock?"}
    ]
)
print(response)
```

------
#### [ Responses API ]

```
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="xai.grok-4.3",
    input="Can you explain the features of Amazon Bedrock?"
)
print(response)
```

------

## Usage Considerations and Limitations
<a name="model-card-xai-grok-4-3-considerations"></a>
+ **Reasoning effort** — Reasoning is always active by default. You can configure effort via the `reasoning` parameter: `{"effort": "none"}` (disables reasoning), `"low"` (default), `"medium"`, or `"high"`. Reasoning content is encrypted and can be returned by passing `include: ["reasoning.encrypted_content"]` in the Responses API request. You can send the encrypted content back in subsequent turns to provide reasoning context for multi-turn conversations. The Chat Completions API does not return reasoning tokens.

  ```
  response = client.responses.create(
      model="xai.grok-4.3",
      reasoning={"effort": "high"},
      include=["reasoning.encrypted_content"],
      input="Explain quantum entanglement simply."
  )
  print(response.output_text)
  ```
+ **Default parameters** — Grok 4.3 uses defaults that differ from the standard OpenAI API specification: `temperature` defaults to `0.7` (not `1`), `top_p` defaults to `0.95` (not `1`), and `max_completion_tokens` defaults to `131072`. Adjust these values explicitly if your application requires different behavior.