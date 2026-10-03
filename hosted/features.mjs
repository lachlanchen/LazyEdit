// Operator configuration, independent of billing and client-requested scopes.
// Invitations grant editing access. Publication is a separately enabled service.
export function accountCapabilities(config, registry, owner) {
  const policy = config.publishing;
  const publishing = policy?.enabled === true && (
    policy.administrators === true && registry.isAdmin(owner) ||
    Array.isArray(policy.accountIds) && policy.accountIds.includes(owner)
  );
  return {editing: true, publishing};
}
