output "cluster_name"         { value = module.eks.cluster_name }
output "ecr_repository_url"   { value = aws_ecr_repository.repo.repository_url }
output "github_oidc_role_arn" { value = aws_iam_role.github_oidc.arn }
