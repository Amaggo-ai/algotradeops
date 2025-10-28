module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "${var.project}-vpc"
  cidr = "10.0.0.0/16"
  azs             = ["${var.region}a","${var.region}b","${var.region}c"]
  private_subnets = ["10.0.1.0/24","10.0.2.0/24","10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24","10.0.102.0/24","10.0.103.0/24"]

  enable_nat_gateway = true
}

resource "aws_ecr_repository" "repo" {
  name                 = "${var.project}-repo"
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration { scan_on_push = true }
}

data "aws_caller_identity" "current" {}

resource "aws_iam_openid_connect_provider" "github" {
  url = "https://token.actions.githubusercontent.com"
  client_id_list = ["sts.amazonaws.com"]
  thumbprint_list = ["6938fd4d98bab03faadb97b34396831e3780aea1"]
}

resource "aws_iam_role" "github_oidc" {
  name = "${var.project}-github-oidc"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Principal = { Federated = aws_iam_openid_connect_provider.github.arn },
      Action = "sts:AssumeRoleWithWebIdentity",
      Condition = {
        StringEquals = { "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com" },
        StringLike   = { "token.actions.githubusercontent.com:sub" = "repo:${var.github_org}/${var.github_repo}:*" }
      }
    }]
  })
}

resource "aws_iam_policy" "ci" {
  name = "${var.project}-ci-policy"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      { Effect="Allow", Action=["ecr:GetAuthorizationToken"], Resource="*" },
      { Effect="Allow", Action=[
          "ecr:BatchCheckLayerAvailability","ecr:CompleteLayerUpload","ecr:DescribeRepositories",
          "ecr:BatchGetImage","ecr:GetDownloadUrlForLayer","ecr:InitiateLayerUpload","ecr:PutImage","ecr:UploadLayerPart"
        ], Resource="*" },
      { Effect="Allow", Action=["eks:DescribeCluster"], Resource="*" }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "attach" {
  role       = aws_iam_role.github_oidc.name
  policy_arn = aws_iam_policy.ci.arn
}

module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.0"

  cluster_name    = "${var.project}-eks"
  cluster_version = var.cluster_version

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  enable_irsa = true

  eks_managed_node_groups = {
    default = {
      ami_type       = "AL2_x86_64"
      instance_types = ["t3.large"]
      min_size = 1
      max_size = 3
      desired_size = 2
    }
  }

  manage_aws_auth_configmap = true
  aws_auth_roles = [{
    rolearn  = aws_iam_role.github_oidc.arn
    username = "github-ci"
    groups   = ["system:masters"]
  }]
}

output "cluster_name"         { value = module.eks.cluster_name }
output "ecr_repository_url"   { value = aws_ecr_repository.repo.repository_url }
output "github_oidc_role_arn" { value = aws_iam_role.github_oidc.arn }
