# Quick Start

Get up and running with VMware vRA CLI in just a few minutes! This guide will walk you through creating your first virtual machine using the CLI.

## Step 1: Authentication

First, authenticate with your vRA environment:

```bash
vra auth login
```

You'll be prompted for:

- **Username**: Your vRA username
- **Password**: Your vRA password (hidden input)
- **URL**: Your vRA server URL (e.g., `https://vra.company.com`)
- **Tenant**: Your vRA tenant (default: `vsphere.local`)

!!! tip "Pro Tip"
    Your credentials are securely stored in your system keyring for future use.

Example:

```bash
$ vra auth login
Username: admin@vsphere.local
Password: ********
vRA URL: https://vra.company.com
Tenant [vsphere.local]: 

✅ Authentication successful!
🔑 Token saved to keyring
```

## Step 2: Explore Available Resources

### List VM Templates

See what VM templates are available:

```bash
vra vm templates
```

### List Projects

Check which projects you have access to:

```bash
vra project list
```

## Step 3: Create Your First VM

Create a new virtual machine:

```bash
vra vm create \
  --template "Ubuntu Server 20.04 LTS" \
  --name "my-first-vm" \
  --project "Development" \
  --description "My first VM created with vRA CLI"
```

!!! info "Command Breakdown"
    - `--template`: The VM template to use
    - `--name`: Unique name for your VM
    - `--project`: Project to deploy the VM in
    - `--description`: Optional description

## Step 4: Monitor VM Creation

Check the status of your VM:

```bash
vra vm status my-first-vm
```

You can also watch the deployment in real-time:

```bash
vra vm watch my-first-vm
```

## Step 5: Manage Your VM

Once your VM is ready, you can perform various operations:

### Get VM Details

```bash
vra vm show my-first-vm
```

### Power Operations

```bash
# Power on
vra vm power-on my-first-vm

# Power off
vra vm power-off my-first-vm

# Restart
vra vm restart my-first-vm
```

### Connect to VM

Get connection information:

```bash
vra vm connect my-first-vm
```

## Step 6: Clean Up

When you're done, delete the VM:

```bash
vra vm delete my-first-vm --confirm
```

## Common Workflows

### Batch Operations

Create multiple VMs at once:

```bash
# Create 5 development VMs
for i in {1..5}; do
  vra vm create \
    --template "Ubuntu Server 20.04 LTS" \
    --name "dev-vm-$i" \
    --project "Development"
done
```

### Configuration File

For complex deployments, use a configuration file:

=== "vm-config.yaml"

    ```yaml
    name: "web-server-001"
    template: "Ubuntu Server 20.04 LTS"
    project: "Production"
    description: "Web server for production environment"
    cpu: 2
    memory: 4096
    disk: 50
    network: "Production-Network"
    tags:
      - environment: production
      - role: web-server
      - owner: ops-team
    ```

=== "Command"

    ```bash
    vra vm create --config vm-config.yaml
    ```

## Interactive Mode

Use interactive mode for guided VM creation:

```bash
vra vm create --interactive
```

This will prompt you through all the options step by step.

## What's Next?

Now that you've created your first VM, explore more features:

1. **[Authentication Guide](../user-guide/authentication.md)** - Advanced authentication options
2. **[VM Management](../user-guide/vm-management.md)** - Complete VM lifecycle management  
3. **[API Reference](../user-guide/api-reference.md)** - Full command reference
4. **[Configuration](configuration.md)** - Customize your CLI experience

## Quick Reference

### Essential Commands

| Command | Description |
|---------|-------------|
| `vra auth login` | Authenticate with vRA |
| `vra vm templates` | List available templates |
| `vra vm create` | Create a new VM |
| `vra vm list` | List your VMs |
| `vra vm status <name>` | Check VM status |
| `vra vm delete <name>` | Delete a VM |
| `vra --help` | Show help |

### Getting Help

Any command can show help with `--help`:

```bash
vra vm create --help
vra auth --help
vra --help
```

!!! success "Congratulations! 🎉"
    You've successfully created and managed your first VM using VMware vRA CLI!
