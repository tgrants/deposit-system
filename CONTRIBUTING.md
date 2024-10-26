# Contributing

As of now, contributions are welcome only from the Deposit System developer team - this includes students who are in this group.

When contributing to the repository, please first discuss the change you want to make via issue or one of our group chats.
If you need any help, please consult the group chat or [@tgrants](https://github.com/tgrants).

## Branch Structure

We use a simple branch structure:

- **main**: Main branch. Should always contain working, tested and documented code.
- **feature/task branches**: New features or fixes should be developed in their own branches.

### Branch Naming Convention

- **Features**: `feature/short-description` (e.g., `feature/better-aerodynamics`)
- **Fixes**: `fix/short-description` (e.g., `fix/device-self-destriction`)

## Workflow

### Issues

Create issues or notify the group for:
- small fixes (e.g. typos, small visual adjustments)
- feature requests
- bugs

### Pull requests

- Fork the repository
	- Click the **Fork** button at the top-right of the [repository page](https://github.com/tgrants/deposit-system).
	- This will create a copy of the repository under your GitHub account.
- Clone the repository from **your fork**
	- `git clone https://github.com/your-username/deposit-system.git`
	- `cd deposit-system`
- Create a branch for your changes
	- `git checkout -b feature/feature-name`
- Make changes and commit in small but meaningful chunks
	- `git add .`
	- `git commit -m "Description of the change"`
- Run linters to ensure your code is formatted properly
	- `pylint .`
- Push your changes to your forked repository
	- `git push origin feature/your-feature-name`
- Once your changes are ready, open a pull request
	- Go to the [main repository](https://github.com/tgrants/deposit-system) on GitHub
	- Click "New pull request"
	- Select your fork and the branch containing your changes as the source, and the original repository's main branch as the destination
	- Add a descriptive title and explain the changes you've made
	- Submit the pull request
