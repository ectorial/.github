import { promises as fs } from 'fs';
import { PLACEHOLDER } from './constants.js';
const githubToken = process.env.GH_TOKEN ? process.env.GH_TOKEN : process.env.GITHUB_TOKEN;

if (!githubToken) {
	throw new Error('githubToken environment variable is not set');
}

// Function to fetch actions with most stars
async function checkIfRepoIsAction(owner, repo) {
	try {
		const response = await fetch(
			`https://api.github.com/repos/${owner}/${repo}/contents/action.yml`,
			{
				headers: {
					Authorization: `Bearer ${githubToken}`,
					Accept: 'application/vnd.github.v3+json',
				},
			}
		);
		return response.status === 200;
	} catch {
		return false;
	}
}

async function getGitHubStats(query, sort = 'stars', order = 'desc', perPage = 10) {
	try {
		const response = await fetch(
			`https://api.github.com/search/repositories?q=${query}&sort=${sort}&order=${order}&per_page=${perPage}`,
			{
				headers: {
					Authorization: `Bearer ${githubToken}`,
					Accept: 'application/vnd.github.v3+json',
				},
			}
		);
		const data = await response.json();
		const { items } = data;

		// Filter only repositories that have action.yml
		const actionRepos = [];
		for (const repo of items) {
			const [owner, name] = repo.full_name.split('/');
			if (await checkIfRepoIsAction(owner, name)) {
				actionRepos.push(repo);
			}
			if (actionRepos.length >= 5) break; // Stop after finding 5 valid actions
		}

		return actionRepos
			.map((action) => {
				return `- [${action.full_name}](${action.html_url}) - ⭐️ ${action.stargazers_count}`;
			})
			.join('\n');
	} catch (error) {
		console.error('Error fetching GitHub stats:', error);
		return '';
	}
}

// Function to update the README
async function updateReadme() {
	try {
		// Read the template file
		const template = await fs.readFile('./profile/README.md.tpl', 'utf8');

		// Replace placeholders in the template

		let content = template.replace(
			PLACEHOLDER.POPULAR,
			await getGitHubStats('topic:github-action', 'stars', 'desc', 5)
		);
		content = template.replace(
			PLACEHOLDER.USED,
			await getGitHubStats('topic:github-action', 'stars', 'desc', 5)
		);

		// Write the processed content to README.md
		await fs.writeFile('./profile/README.md', content, 'utf8');

		console.log('README.md has been updated successfully');
	} catch (error) {
		console.error('Error updating README:', error);
		process.exit(1);
	}
}

// Run the update function
updateReadme();
