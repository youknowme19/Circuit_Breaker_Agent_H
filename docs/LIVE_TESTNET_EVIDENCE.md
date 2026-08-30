# Monad Testnet Live Transaction Verification Evidence

> **Demonstration of Real On-Chain Financial Transfer via TrueForge → FastMCP → Circuit Breaker → MonadTestnetAdapter.**

---

## On-Chain Verification Parameters

| Property | Value |
| :--- | :--- |
| **Network Name** | Monad Testnet |
| **Chain ID** | `10143` |
| **Native Asset** | `MON` |
| **RPC Endpoint** | `https://testnet-rpc.monad.xyz` |
| **Block Explorer** | `https://testnet.monadexplorer.com` |
| **Verification Status** | **`CONFIRMED`** |
| **Verification Date** | August 28, 2026 |

---

## On-Chain Evidence Receipt

| Field | Value |
| :--- | :--- |
| **Transaction Hash** | `0x2d900118d58606204d0cf9a257f4f889203f6eee40198d000f98b20927ff446c` |
| **Block Number** | `#57687057` |
| **Receipt Status** | **`1` (`CONFIRMED`)** |
| **From Address (Sender)** | `0xa7c965820d4933dBe9F71fE665A4D0adAE98aD06` |
| **To Address (Recipient)** | `0x57d1Cf3D387de087Eda90a1cC81eAc608F7a8f55` |
| **Transfer Amount** | **`0.01 MON`** |
| **Gas Used** | `21,000 units` |
| **Monad Explorer Link** | [https://testnet.monadexplorer.com/tx/0x2d900118d58606204d0cf9a257f4f889203f6eee40198d000f98b20927ff446c](https://testnet.monadexplorer.com/tx/0x2d900118d58606204d0cf9a257f4f889203f6eee40198d000f98b20927ff446c) |

---

## Replay Defense Verification

Following successful broadcast and block confirmation, re-submitting the exact same authorization token `TOKEN-LIVE-4ef4ef` to the Execution Gate resulted in:

```text
EXECUTION_REFUSED — Authorization token TOKEN-LIVE-4ef4ef has already been consumed.
```

This confirms the single-use atomic lock invariant:
$$\text{ONE AUTHORIZATION} \longrightarrow \text{EXACTLY ONE FINANCIAL EXECUTION}$$
