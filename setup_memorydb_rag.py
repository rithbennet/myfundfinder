#!/usr/bin/env python3
"""
Setup Amazon MemoryDB for Redis with vector search
"""

import boto3
import json

def create_memorydb_cluster():
    """Create MemoryDB cluster for vector storage"""
    
    memorydb = boto3.client('memorydb')
    
    cluster_name = "rag-vectors"
    
    try:
        # Create subnet group first
        ec2 = boto3.client('ec2')
        vpcs = ec2.describe_vpcs(Filters=[{'Name': 'is-default', 'Values': ['true']}])
        
        if not vpcs['Vpcs']:
            print("❌ No default VPC found")
            return None
            
        vpc_id = vpcs['Vpcs'][0]['VpcId']
        
        # Get subnets
        subnets = ec2.describe_subnets(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
        subnet_ids = [subnet['SubnetId'] for subnet in subnets['Subnets'][:2]]
        
        # Create subnet group
        try:
            memorydb.create_subnet_group(
                SubnetGroupName=f"{cluster_name}-subnet-group",
                Description="Subnet group for RAG vectors",
                SubnetIds=subnet_ids
            )
            print("✅ Created subnet group")
        except memorydb.exceptions.SubnetGroupAlreadyExistsFault:
            print("ℹ️ Subnet group already exists")
        
        # Create cluster
        response = memorydb.create_cluster(
            ClusterName=cluster_name,
            NodeType='db.t4g.small',
            Description='RAG vector storage cluster',
            NumShards=1,
            SubnetGroupName=f"{cluster_name}-subnet-group",
            SecurityGroupIds=[],  # Will use default
            Port=6379
        )
        
        print(f"✅ Creating MemoryDB cluster: {cluster_name}")
        print(f"📊 Status: {response['Cluster']['Status']}")
        print("⏳ Cluster creation takes 10-15 minutes...")
        
        return cluster_name
        
    except Exception as e:
        print(f"❌ Error creating MemoryDB cluster: {e}")
        return None

def get_cluster_endpoint(cluster_name: str):
    """Get cluster endpoint when ready"""
    memorydb = boto3.client('memorydb')
    
    try:
        response = memorydb.describe_clusters(ClusterName=cluster_name)
        cluster = response['Clusters'][0]
        
        if cluster['Status'] == 'available':
            endpoint = cluster['ClusterEndpoint']['Address']
            port = cluster['ClusterEndpoint']['Port']
            print(f"✅ Cluster ready: {endpoint}:{port}")
            return f"{endpoint}:{port}"
        else:
            print(f"⏳ Cluster status: {cluster['Status']}")
            return None
            
    except Exception as e:
        print(f"❌ Error getting cluster info: {e}")
        return None

if __name__ == "__main__":
    print("🚀 Setting up Amazon MemoryDB for RAG vectors")
    print("=" * 50)
    
    cluster_name = create_memorydb_cluster()
    
    if cluster_name:
        print(f"\n📋 Next steps:")
        print(f"1. Wait for cluster to be 'available' (10-15 minutes)")
        print(f"2. Run: python setup_memorydb_rag.py --check {cluster_name}")
        print(f"3. Use the endpoint in your RAG application")
    else:
        print("❌ Failed to create cluster")
