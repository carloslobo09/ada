import { useMutation, useQueryClient } from "@tanstack/react-query";
import { resetPassword } from "@/features/users/api/usersClient";

interface ResetInput {
  userId: string;
  newPassword: string;
}

export function useResetPassword() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ userId, newPassword }: ResetInput) =>
      resetPassword(userId, { new_password: newPassword }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] });
    },
  });
}
