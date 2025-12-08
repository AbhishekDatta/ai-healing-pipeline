# 🤖 AI-Powered Self-Healing CI/CD Pipeline

> An autonomous AI agent that detects, investigates, and fixes CI/CD pipeline failures using Multi-LLM architecture.

## 🌟 Project Goals
- Build production-grade CI/CD pipeline
- Implement truly agentic AI for autonomous problem-solving
- Deploy on cost-optimized AWS infrastructure (<$10/month)
- Demonstrate self-healing capabilities

## 🛠️ Tech Stack
- **Infrastructure**: Terraform, AWS Spot Instances, K3s
- **CI/CD**: GitHub Actions
- **Security**: Trivy, Snyk, OPA
- **Observability**: Prometheus, Grafana, Loki
- **AI**: Claude Sonnet 4, GPT-4o, Gemini 2.0 Flash, Perplexity Sonar
- **Agent**: LangGraph, FastAPI, ChromaDB

## 📅 Development Timeline
Week 1: Foundation & Infrastructure  
Week 2: AI Agent Development  
Week 3: Content Creation & Launch

## 🚀 Status
**Day 1**: Environment setup & learning kickoff ✅


## 📊 Day 2 Progress

### ✅ Completed
- Terraform infrastructure (VPC, subnet, security groups)
- AWS Spot instance deployment (t3.small, $0.006/hour)
- K3s cluster installation via bootstrap script
- Docker, Helm, Python 3.11 configured
- kubectl access from local Mac
- Tested destroy/apply cycle

### 🏗️ Infrastructure
- **Region**: us-east-2 (Ohio)
- **Instance**: t3.small Spot (~70% cheaper than on-demand)
- **OS**: Amazon Linux 2023 (kernel 6.1)
- **K3s**: Lightweight Kubernetes
- **State**: Stored in S3 with DynamoDB locking

### 💰 Current Costs
- **Daily**: ~$0.05 (8 hours × $0.006/hour)
- **Monthly**: ~$1.50
- **State Storage**: <$0.10/month

### 🎯 Next Steps (Day 3)
- Deploy Online Boutique application
- Configure namespaces and resource limits
- Verify all 11 microservices running


## 📊 Day 3 Progress - COMPLETED ✅

### ✅ Achievements
- **Automated Infrastructure Deployment**: Single `terraform apply` command deploys complete system
- **K3s Cluster**: Configured with proper TLS certificates for external kubectl access
- **Online Boutique Application**: 11 microservices auto-deployed and verified
- **CoreDNS Resolution**: Fixed initialization timing issues through systematic troubleshooting
- **Bootstrap Automation**: Comprehensive script handles all setup in 7-10 minutes

### 🏗️ Infrastructure Details
- **Instance Type**: t3.small (2 vCPU, 2GB RAM)
- **Cost**: ~$0.05/day = $1.50/month (well under $10 budget)
- **Deployment Time**: 7-10 minutes from `terraform apply` to working application
- **Access**: Application available at http://<INSTANCE_IP>:30001

### 🛍️ Application Architecture
- **Services**: 11 microservices + Redis
- **Languages**: Go, Python, Node.js, Java, C#
- **Namespace**: online-boutique
- **Access Method**: NodePort 30001 (adapted from LoadBalancer for K3s)
- **Access**: http://<INSTANCE_IP>:30001
- **Health**: http://<INSTANCE_IP>:30001/_healthz

### 🔧 Technical Learnings
1. **K3s Configuration**: Pre-created `/etc/rancher/k3s/config.yaml` essential for proper CoreDNS initialization
2. **CoreDNS Timing**: 30-second wait sufficient; complex health checks unnecessary
3. **Certificate Management**: TLS SANs must include both public and private IPs for external kubectl access
4. **Resource Optimization**: t3.small adequate for development; reduced resource requests to 50m CPU, 64Mi memory per service
5. **Troubleshooting Methodology**: Systematic comparison of working vs. failing configurations proved most effective

### 📁 Project Structure
```
ai-healing-pipeline/
├── terraform/
│   ├── main.tf                  # Infrastructure as Code
│   ├── scripts/
│   │   └── bootstrap.sh         # Automated setup script
├── k8s/
│   └── online-boutique/
│       └── k3s-manifests.yaml   # Kubernetes manifests (created by bootstrap)
├── docs/
│   └── online-boutique-architecture.md
└── README.md
```

### 🔄 Daily Workflow
```bash
# Morning: Start infrastructure
cd ~/ai-healing-pipeline/terraform
terraform apply -auto-approve
# Wait 7-10 minutes for complete setup

# Verify deployment
export KUBECONFIG=~/.kube/config-k3s
kubectl get pods -n online-boutique  # All should be Running
curl http://$(terraform output -raw instance_public_ip):30001/_healthz  # Should return "ok"

# Evening: Tear down to save costs
terraform destroy -auto-approve
```

### 💡 Key Insights from Day 3
The most valuable lesson was **replicating successful manual processes exactly** rather than over-engineering automation. When automated deployment failed but manual deployment succeeded, the solution was to match the automation to the manual process precisely—not to add complexity. This principle will guide future development.

### 🐛 Issues Resolved
- ❌ CoreDNS "Failed to watch" API errors → ✅ Fixed with proper config.yaml creation
- ❌ Certificate validation errors → ✅ Fixed with TLS SAN configuration
- ❌ Timing issues with EIP detection → ✅ Simplified wait logic
- ❌ Over-complex health checks → ✅ Replaced with simple 30-second wait

### 🔍 Common Issues & Solutions

**Issue**: CoreDNS not becoming ready
**Solution**: Ensure `/etc/rancher/k3s/config.yaml` exists before K3s installation

**Issue**: kubectl certificate validation failures
**Solution**: Verify TLS SANs include public IP in K3s config

**Issue**: Application shows "connection refused" DNS errors
**Solution**: Wait 30 seconds after K3s start before deploying applications

**Issue**: Pods show "ImagePullBackOff"
**Solution**: Check internet connectivity; gcr.io images require external access

### 🎯 Day 4 Preview - CI/CD Pipeline Development
- Build GitHub Actions workflow
- Implement automated testing (unit + integration)
- Create Docker image build pipeline
- Add security scanning (Trivy, Snyk)
- Setup automated deployment triggers
- SBOM generation
---
Built with ❤️ as part of DevOps upskilling journey